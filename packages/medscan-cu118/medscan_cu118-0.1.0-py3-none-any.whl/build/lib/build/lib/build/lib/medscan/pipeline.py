# pipeline.py
# ============================================================================
#  End-to-end trainingspipeline:
#  • Laadt en normaliseert afbeeldingen 
#  • Ondersteunt single-channel inputs door duplicatie naar 3-kanalen
#  • Gebruikt torch.amp.GradScaler en torch.amp.autocast volgens nieuwe API
#  • Twee modi:
#      – train_per_label=True: separaat SingleHead-model per target (met herordening per backbone)
#      – train_per_label=False: één MultiHead-model, met aparte early-stopping per head
#  • Print trainings- en validatie-statistieken per epoch (ValLoss)
#  • predict(): voegt per target een kolom "Label_<target>" toe
#  • evaluate(): berekent alleen de gecallde metrics en toont gecallde plots:
#      – confusion_matrix
#      – loss_vs_epoch (train + val loss)
#      – lr_vs_epoch (learning rate)
# ============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union

import os
import math
import inspect
import itertools

import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms.functional import resize, normalize
from torchvision.io import read_image, ImageReadMode
import matplotlib.pyplot as plt

from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    f1_score,
    confusion_matrix,
)

from .config import PreprocessConfig, TrainConfig  # pragma: no cover

from .transform import augment_and_balance



#  1 · BACKBONE HELPER


def _infer_nf_runtime(model: nn.Module, input_size: int = 224) -> int:
    """Stuur een dummy door het netwerk om het feature-aantal te bepalen."""
    device = next(model.parameters()).device
    dummy = torch.zeros((1, 3, input_size, input_size), device=device)
    with torch.no_grad():
        out = model(dummy)
    if out.ndim == 4:  # (B,C,H,W) → (B, C*H*W)
        out = out.flatten(1)
    return out.shape[1]


def _strip_head_and_get_nf(model: nn.Module) -> int:
    """
    Verwijder de classificatiekop van bekende torchvision-backbones
    en retourneer de breedte van het feature-vector.
    """
    if hasattr(model, "classifier"):
        head = model.classifier
        if isinstance(head, nn.Sequential):
            nf = next(ly.in_features for ly in head if isinstance(ly, nn.Linear))
        elif isinstance(head, nn.Linear):
            nf = head.in_features
        else:  # pragma: no cover
            raise RuntimeError("Onbekend classifier-type")
        model.classifier = nn.Identity()
        return nf

    if hasattr(model, "fc"):
        nf = model.fc.in_features
        model.fc = nn.Identity()
        return nf

    return _infer_nf_runtime(model)


def backbone(name: str, pretrained: bool = True) -> Tuple[nn.Module, int]:
    """
    Maakt een backbone door naam (bv. 'resnet34', 'mobilenet_v3_large', 'scratch')
    en geeft het (model, num_features) paar terug.
    """
    if name == "scratch":
        cnn = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
        return cnn, 64

    from torchvision import models  # lazy import
    if not hasattr(models, name):
        raise ValueError(f"Onbekende backbone-naam: {name!r}")

    ctor = getattr(models, name)
    sig = inspect.signature(ctor)
    kw: Dict[str, Any] = {}
    if pretrained and "weights" in sig.parameters:
        kw["weights"] = "IMAGENET1K_V1"

    m = ctor(**kw)
    nf = _strip_head_and_get_nf(m)
    return m, nf


#  2 · MODEL DEFINITIES

class SingleHead(nn.Module):
    """Backbone + (optioneel) Dropout + Linear classifier (+ contextfeatures)."""

    def __init__(
        self,
        bb: nn.Module,
        nf: int,
        out_dim: int,
        proj_dim: int = 0,
        dropout_rate: float | None = None,
    ) -> None:
        super().__init__()
        layers: List[nn.Module] = []
        if dropout_rate:
            layers.append(nn.Dropout(dropout_rate))
        layers.append(nn.Linear(nf + proj_dim, out_dim))
        self.bb = bb
        self.classifier = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, proj: torch.Tensor | None = None) -> torch.Tensor:
        z = self.bb(x)
        if z.ndim > 2:  # (B,C,H,W) → (B,-1)
            z = torch.flatten(z, 1)
        if proj is not None and proj.numel():
            z = torch.cat([z, proj], dim=1)
        return self.classifier(z)


class MultiHead(nn.Module):
    """
    Eén backbone met meerdere heads (één head per target). 
    Elke head is een Linear (met eventueel Dropout) bovenop gedeelde features.
    """

    def __init__(
        self,
        bb: nn.Module,
        nf: int,
        out_dims: Dict[str, int],
        proj_dim: int = 0,
        dropout_rate: float | None = None,
    ) -> None:
        super().__init__()
        self.bb = bb
        self.heads = nn.ModuleDict()
        for t, od in out_dims.items():
            layers: List[nn.Module] = []
            if dropout_rate:
                layers.append(nn.Dropout(dropout_rate))
            layers.append(nn.Linear(nf + proj_dim, od))
            self.heads[t] = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, proj: torch.Tensor | None = None) -> Dict[str, torch.Tensor]:
        z = self.bb(x)
        if z.ndim > 2:
            z = torch.flatten(z, 1)
        if proj is not None and proj.numel():
            z = torch.cat([z, proj], dim=1)
        out: Dict[str, torch.Tensor] = {}
        for t, head in self.heads.items():
            out[t] = head(z)
        return out


#  3 · DATASET

class _Dataset(Dataset):
    """
    Wrapt een DataFrame dat minstens kolom 'img_path' bevat.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        target_cols: List[str],
        context_cols: Sequence[str],
        input_size: int,
        normalize_means: Tuple[float, float, float] = (0.485, 0.456, 0.406),
        normalize_stds: Tuple[float, float, float] = (0.229, 0.224, 0.225),
    ) -> None:
        self.df = df.reset_index(drop=True)
        self.img_paths = df["img_path"].tolist()
        self.target_cols = target_cols
        self.context = (
            df[context_cols].astype("float32").values if context_cols else None
        )
        self.input_size = input_size
        self.normalize_means = normalize_means
        self.normalize_stds = normalize_stds

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, Dict[str, Any]]:
        img_path = self.img_paths[idx]
        img = read_image(img_path, ImageReadMode.RGB).float() / 255.0  # (C,H,W) ∈ [0,1]

        if img.shape[0] == 1:
            img = img.repeat(3, 1, 1)

        # Resize 
        img = resize(img, [self.input_size, self.input_size])

        # Normaliseer
        img = normalize(img, mean=self.normalize_means, std=self.normalize_stds)

        # 
        y_dict: Dict[str, Any] = {}
        for t in self.target_cols:
            y_dict[t] = self.df.loc[idx, t]

        # Context-features wanneer gecalled
        if self.context is not None:
            proj = torch.from_numpy(self.context[idx])
        else:
            proj = torch.empty(0)

        return img, proj, y_dict


#  4 · PIPELINE

class Pipeline:
    """
    Eén klasse die alles doet:
      • fit()      : trainen (per target per backbone) of MultiHead met aparte early-stopping per head
      • predict()  : voorspellingen toevoegen als kolommen "Label_<target>"
      • evaluate():
          – confusion_matrix
          – loss_vs_epoch (train + val loss)
          – lr_vs_epoch (learning rate)
      • save()/load()
    """

    def __init__(
        self,
        preprocess_config: PreprocessConfig,
        train_config: TrainConfig,
        targets: List[str],
    ) -> None:
        self.pre_cfg = preprocess_config
        self.train_cfg = train_config
        self.targets = targets
        self.device = torch.device(train_config.device)
        self.mixed = bool(train_config.mixed_precision and
                          self.device.type == "cuda")

        # Gaat gevuld worden in fit()
        self.models: Dict[str, nn.Module] = {}
        self.out_dims: Dict[str, int] = {}

        # Tracking voor plots:
        self.train_loss_history: Dict[str, List[float]] = {}  # per target
        self.val_loss_history: Dict[str, List[float]] = {}    # per target
        self.lr_history: Union[List[float], Dict[str, List[float]]] = []  # MultiHead: lijst; per-label: dict

    def fit(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame | None = None,
    ) -> None:
        """
        Als train_cfg.train_per_label = True:
          – voor elk pretrained model: train alle targets met SingleHead
        Als train_cfg.train_per_label = False:
          – maak één MultiHead-model (gedeelde backbone + heads),
            train alle targets tegelijkertijd, met aparte early-stopping per head.
        """

        # AUGMENTATIE en BALANCING 
        # Voorkom balanceren zonder augmentatie
        if getattr(self.pre_cfg, "balance_on", False) and not getattr(self.pre_cfg, "augment", False):
            raise ValueError("Balancing requires 'augment=True'. Please set both 'augment=True' and 'balance_on=True' in PreprocessConfig als je wil balanceren.")

        if getattr(self.pre_cfg, "augment", False) or getattr(self.pre_cfg, "balance_on", False):
            # Gebruik 'augmented_image_path' uit de PreprocessConfig; fallback naar 'augmented_images'
            base_out = getattr(self.pre_cfg, "augmented_image_path", "augmented_images")
            os.makedirs(base_out, exist_ok=True)

            for t in self.targets:
                output_dir = os.path.join(base_out, t)
                os.makedirs(output_dir, exist_ok=True)

                try:
                    train_df = augment_and_balance(
                        df_in=train_df,
                        config=self.pre_cfg,
                        target_col=t,
                        output_dir=output_dir,
                        seed=42,
                        img_column="img_path"
                    )
                    print(f"> Augmentatie/balancing uitgevoerd voor target '{t}', output in '{output_dir}'")
                except Exception as e:
                    print(f"> Fout bij augment_and_balance voor target '{t}': {e}. Overslaan.")


        context_cols = list(
            itertools.chain(
                getattr(self.pre_cfg, "onehot_columns", []),
                getattr(self.pre_cfg, "context_labels", []),
            )
        )

        scaler = torch.amp.GradScaler(enabled=self.mixed)
        autocast_device = "cuda" if self.mixed else "cpu"

        # 0) Bepaal output-dimensies per target uit train_df (drop NaN per target)
        for t in self.targets:
            unique_vals = train_df[t].dropna().unique()
            classes = sorted(int(x) for x in unique_vals)
            self.out_dims[t] = 1 if len(classes) <= 2 else len(classes)


        for t in self.targets:
            self.train_loss_history[t] = []
            self.val_loss_history[t] = []

        # CASE A: Één MultiHead-model voor alle targets
        if not getattr(self.train_cfg, "train_per_label", False):
            # --- 1) Backbone + heads initieel laden (eerste pretrained) ---
            bb_name = self.train_cfg.pretrained_models[0]
            bb, nf = backbone(bb_name, pretrained=True)
            multi_model = MultiHead(
                bb=bb,
                nf=nf,
                out_dims=self.out_dims,
                proj_dim=len(context_cols),
                dropout_rate=(self.train_cfg.dropout_rate
                              if getattr(self.train_cfg, "dropout", False) else None),
            ).to(self.device)

            if self.mixed:
                multi_model = multi_model.to(memory_format=torch.channels_last)

            # ** OPTIMIZER ZONDER weight_decay **
            optimizer = torch.optim.Adam(
                multi_model.parameters(),
                lr=self.train_cfg.learning_rate,
            )

            # ** SCHEDULER VERWIJDERD **

            # Loss-functies per target
            loss_fns: Dict[str, nn.Module] = {}
            for t, od in self.out_dims.items():
                loss_fns[t] = (nn.BCEWithLogitsLoss()
                               if od == 1 else nn.CrossEntropyLoss())

            # DataLoaders: train en val
            tr_ds = _Dataset(
                train_df,
                self.targets,
                context_cols,
                input_size=self.train_cfg.input_size,
            )
            tr_ld = DataLoader(
                tr_ds,
                batch_size=self.train_cfg.batch_size,
                shuffle=True,
                num_workers=0,
            )

            va_ds = (
                _Dataset(val_df, self.targets, context_cols, input_size=self.train_cfg.input_size)
                if val_df is not None and len(val_df)
                else None
            )
            va_ld = (
                DataLoader(
                    va_ds,
                    batch_size=self.train_cfg.batch_size,
                    shuffle=False,
                    num_workers=0,
                ) if va_ds is not None else None
            )

            # Voor elk target: best val_loss, bad_count, active_flag
            best_loss: Dict[str, float] = {t: float("inf") for t in self.targets}
            bad_count: Dict[str, int] = {t: 0 for t in self.targets}
            active: Dict[str, bool] = {t: True for t in self.targets}
            patience = getattr(self.train_cfg, "early_stopping_patience", 0)

            # Init lr_history als lijst
            self.lr_history = []

            # 2) Train-loop (zelfde model, alle heads samen)
            for ep in range(1, self.train_cfg.epochs + 1):
                # --- TRAINING EPOCH ---
                multi_model.train()
                total_train_loss: Dict[str, float] = {t: 0.0 for t in self.targets}
                total_samples: int = 0

                for x, proj, y_dict in tr_ld:
                    optimizer.zero_grad(set_to_none=True)
                    x = x.to(self.device)
                    # Verzamel per-target y_tensor
                    y_tensors: Dict[str, torch.Tensor] = {}
                    for t in self.targets:
                        if self.out_dims[t] == 1:
                            y_tensors[t] = torch.tensor(
                                y_dict[t], dtype=torch.float32, device=self.device
                            )
                        else:
                            y_tensors[t] = torch.tensor(
                                y_dict[t], dtype=torch.long, device=self.device
                            )
                    proj_t = (proj.to(self.device) if proj.numel() else None)

                    with torch.amp.autocast(device_type=autocast_device):
                        logits_dict = multi_model(x, proj_t)

                        # Per-target loss, alleen voor actieve heads en waar y != NaN
                        losses: List[torch.Tensor] = []
                        for t in self.targets:
                            if not active[t]:
                                continue
                            y_t = y_tensors[t]
                            mask = ~torch.isnan(y_t)
                            if not mask.any():
                                continue
                            logit = logits_dict[t]
                            if self.out_dims[t] == 1:
                                l = loss_fns[t](logit.squeeze(1)[mask], y_t[mask])
                            else:
                                l = loss_fns[t](logit[mask], y_t[mask].long())
                            losses.append(l)
                            total_train_loss[t] += l.item() * mask.sum().item()

                        if not losses:
                            continue

                        loss_all = torch.stack(losses).mean()

                    scaler.scale(loss_all).backward()
                    scaler.step(optimizer)
                    scaler.update()

                    total_samples += x.size(0)

                # Gem. train loss per target
                avg_train_loss = {
                    t: (total_train_loss[t] / total_samples if total_samples else float("nan"))
                    for t in self.targets
                }
                for t in self.targets:
                    self.train_loss_history[t].append(avg_train_loss[t])

                # ** GEEN scheduler.step() **

                # VAL EPOCH
                avg_val_loss: Dict[str, float] = {t: float("nan") for t in self.targets}
                if va_ld is not None:
                    multi_model.eval()
                    val_accum: Dict[str, float] = {t: 0.0 for t in self.targets}
                    val_counts: Dict[str, int] = {t: 0 for t in self.targets}
                    with torch.no_grad(), torch.amp.autocast(device_type=autocast_device):
                        for x_v, proj_v, yv_dict in va_ld:
                            x_v = x_v.to(self.device)
                            yv_tensors: Dict[str, torch.Tensor] = {}
                            for t in self.targets:
                                if self.out_dims[t] == 1:
                                    yv_tensors[t] = torch.tensor(
                                        yv_dict[t], dtype=torch.float32, device=self.device
                                    )
                                else:
                                    yv_tensors[t] = torch.tensor(
                                        yv_dict[t], dtype=torch.long, device=self.device
                                    )
                            proj_v_t = (proj_v.to(self.device) if proj_v.numel() else None)
                            logits_v = multi_model(x_v, proj_v_t)

                            for t in self.targets:
                                if not active[t]:
                                    continue
                                yv = yv_tensors[t]
                                mask_v = ~torch.isnan(yv)
                                if not mask_v.any():
                                    continue
                                logit_v = logits_v[t]
                                if self.out_dims[t] == 1:
                                    lv = loss_fns[t](logit_v.squeeze(1)[mask_v], yv[mask_v])
                                else:
                                    lv = loss_fns[t](logit_v[mask_v], yv[mask_v].long())
                                count = mask_v.sum().item()
                                val_accum[t] += lv.item() * count
                                val_counts[t] += count

                    for t in self.targets:
                        if val_counts[t]:
                            avg_val_loss[t] = val_accum[t] / val_counts[t]
                            self.val_loss_history[t].append(avg_val_loss[t])

                stats = "  ".join(
                    f"{t} TrainLoss={avg_train_loss[t]:.4f} ValLoss={avg_val_loss[t]:.4f}"
                    for t in self.targets
                )
                print(f"Epoch {ep}/{self.train_cfg.epochs}  {stats}")

                # EARLY STOPPING PER HEAD
                all_inactive = True
                for t in self.targets:
                    if not active[t]:
                        continue
                    if not math.isnan(avg_val_loss[t]) and avg_val_loss[t] < best_loss[t]:
                        best_loss[t] = avg_val_loss[t]
                        bad_count[t] = 0
                        # sla een kopie van de huidige state op voor deze head voor als je later het model weer gaat laden
                        if "best_states" not in locals():
                            best_states: Dict[str, Dict[str, torch.Tensor]] = {}
                        best_states[t] = {
                            k: v.clone().cpu() for k, v in multi_model.state_dict().items()
                        }
                    else:
                        bad_count[t] += 1
                        if bad_count[t] >= patience:
                            active[t] = False
                    all_inactive = all_inactive and not active[t]

                # Stop training als alle heads inactief zijn
                if all_inactive:
                    print(f"Alle heads hebben early-stopping bereikt op epoch {ep}.")
                    break

            # EINDE TRAIN-LOOP
            # Laad voor elke head de best state
            final_state = multi_model.state_dict()
            for t in self.targets:
                if t in best_states:
                    for k, v in best_states[t].items():
                        final_state[k] = v.to(self.device)
            multi_model.load_state_dict(final_state)
            multi_model.eval()
            # Sla MultiHead-model op onder "_multi"
            self.models["_multi"] = multi_model

        # CASE B: Eén model per target
        else:
            # Houd per target de beste state bij
            global_best_loss: Dict[str, float] = {t: float("inf") for t in self.targets}
            global_best_state: Dict[str, Dict[str, torch.Tensor]] = {t: {} for t in self.targets}
            global_best_model_name: Dict[str, str] = {t: "" for t in self.targets}

            # Per target lr histories
            per_target_lr: Dict[str, List[float]] = {t: [] for t in self.targets}

            # Voor elke backbone model eerst alle targets trainen
            for bb_name in self.train_cfg.pretrained_models:
                try:
                    bb, nf = backbone(bb_name, pretrained=True)
                except Exception as e:
                    print(f"Error bij laden backbone {bb_name}: {e}. Oversla.")
                    continue

                for tgt in self.targets:
                    tr_sub = train_df.dropna(subset=[tgt]).copy()
                    va_sub = (val_df.dropna(subset=[tgt]).copy()
                              if val_df is not None else None)

                    if tr_sub.empty:
                        print(f"Geen trainingsdata voor target {tgt}, oversla.")
                        continue

                    tr_ds = _Dataset(
                        tr_sub,
                        [tgt],
                        context_cols,
                        input_size=self.train_cfg.input_size,
                    )
                    tr_ld = DataLoader(
                        tr_ds,
                        batch_size=self.train_cfg.batch_size,
                        shuffle=True,
                        num_workers=0,
                    )

                    va_ds = (
                        _Dataset(va_sub, [tgt], context_cols, input_size=self.train_cfg.input_size)
                        if va_sub is not None and len(va_sub) else None
                    )
                    va_ld = (
                        DataLoader(
                            va_ds,
                            batch_size=self.train_cfg.batch_size,
                            shuffle=False,
                            num_workers=0,
                        ) if va_ds is not None else None
                    )

                    out_dim = self.out_dims[tgt]
                    loss_fn = (nn.BCEWithLogitsLoss()
                               if out_dim == 1 else nn.CrossEntropyLoss())

                    # Initialiseer SingleHead voor deze backbone en target
                    try:
                        model = SingleHead(
                            bb,
                            nf,
                            out_dim,
                            proj_dim=len(context_cols),
                            dropout_rate=(self.train_cfg.dropout_rate
                                          if getattr(self.train_cfg, "dropout", False) else None),
                        ).to(self.device)
                    except Exception as e:
                        print(f"Error bij initialiseren SingleHead {bb_name} voor {tgt}: {e}. Oversla.")
                        continue

                    if self.mixed:
                        model = model.to(memory_format=torch.channels_last)

                    # ** OPTIMIZER ZONDER weight_decay **
                    optimizer = torch.optim.Adam(
                        model.parameters(),
                        lr=self.train_cfg.learning_rate,
                    )

                    # ** SCHEDULER VERWIJDERD **

                    best_loss_bb = float("inf")
                    best_states_bb: Dict[str, torch.Tensor] = {}
                    bad = 0
                    patience = getattr(self.train_cfg, "early_stopping_patience", 0)

                    self.train_loss_history[tgt] = []
                    self.val_loss_history[tgt] = []

                    for ep in range(1, self.train_cfg.epochs + 1):
                        model.train()
                        epoch_loss = 0.0
                        total_samples = 0

                        for x, proj, y_dict in tr_ld:
                            optimizer.zero_grad(set_to_none=True)

                            x = x.to(self.device)
                            if out_dim == 1:
                                y_tensor = torch.tensor(
                                    y_dict[tgt], dtype=torch.float32, device=self.device
                                )
                            else:
                                y_tensor = torch.tensor(
                                    y_dict[tgt], dtype=torch.long, device=self.device
                                )

                            proj_t = (proj.to(self.device) if proj.numel() else None)

                            with torch.amp.autocast(device_type=autocast_device):
                                logits = model(x, proj_t)
                                if out_dim == 1:
                                    loss = loss_fn(logits.squeeze(1), y_tensor)
                                else:
                                    loss = loss_fn(logits, y_tensor)

                            scaler.scale(loss).backward()
                            scaler.step(optimizer)
                            scaler.update()

                            bs = x.size(0)
                            epoch_loss += loss.item() * bs
                            total_samples += bs

                        # Gem. train loss voor target
                        train_loss = epoch_loss / total_samples if total_samples else float("nan")
                        self.train_loss_history[tgt].append(train_loss)

                        # ** GEEN scheduler.step() **
                        # ** GEEN lr_history update **

                        # Validatie
                        val_loss = float("nan")
                        if va_ld is not None and len(va_ld):
                            model.eval()
                            val_epoch_loss = 0.0
                            val_samples = 0
                            with torch.no_grad(), torch.amp.autocast(device_type=autocast_device):
                                for x_v, proj_v, yv_dict in va_ld:
                                    x_v = x_v.to(self.device)
                                    if out_dim == 1:
                                        yv_tensor = torch.tensor(
                                            yv_dict[tgt], dtype=torch.float32, device=self.device
                                        )
                                    else:
                                        yv_tensor = torch.tensor(
                                            yv_dict[tgt], dtype=torch.long, device=self.device
                                        )

                                    proj_v_t = (proj_v.to(self.device) if proj_v.numel() else None)
                                    logits_v = model(x_v, proj_v_t)
                                    if out_dim == 1:
                                        loss_v = loss_fn(logits_v.squeeze(1), yv_tensor)
                                    else:
                                        loss_v = loss_fn(logits_v, yv_tensor)

                                    bs_v = x_v.size(0)
                                    val_epoch_loss += loss_v.item() * bs_v
                                    val_samples += bs_v

                            val_loss = val_epoch_loss / val_samples if val_samples else float("nan")
                            self.val_loss_history[tgt].append(val_loss)

                        print(
                            f"[{tgt} | {bb_name}] "
                            f"Epoch {ep}/{self.train_cfg.epochs}  "
                            f"TrainLoss={train_loss:.4f}  ValLoss={val_loss:.4f}"
                        )

                        if not math.isnan(val_loss) and val_loss < best_loss_bb:
                            best_loss_bb = val_loss
                            best_states_bb = {k: v.clone() for k, v in model.state_dict().items()}
                            bad = 0
                        else:
                            bad += 1
                            if bad >= patience:
                                print(f"Early stopping {tgt} op epoch {ep}")
                                break

                    # Vergelijk met globale best per target
                    if best_loss_bb < global_best_loss[tgt]:
                        global_best_loss[tgt] = best_loss_bb
                        global_best_state[tgt] = best_states_bb
                        global_best_model_name[tgt] = bb_name

                    del model, optimizer
                    torch.cuda.empty_cache()

            for tgt in self.targets:
                if not global_best_state[tgt]:
                    raise RuntimeError(f"Er is geen modelstate gevonden voor target {tgt!r}")
                bb_final, nf_final = backbone(global_best_model_name[tgt], pretrained=False)
                best_net = SingleHead(
                    bb_final,
                    nf_final,
                    self.out_dims[tgt],
                    proj_dim=len(context_cols),
                    dropout_rate=(self.train_cfg.dropout_rate
                                  if getattr(self.train_cfg, "dropout", False) else None),
                ).to(self.device)
                best_net.load_state_dict(global_best_state[tgt])
                best_net.eval()
                self.models[tgt] = best_net

            # ** GEEN lr_history opslaan, want we tracken alleen lr in geval van scheduler **


    #  PREDICT
    def predict(self, test_df: pd.DataFrame) -> pd.DataFrame:
        """
        Voegt per target een kolom 'Label_<target>' toe aan test_df:
          • Als train_per_label = True: voorspelt met elk target-specifiek model.
          • Als train_per_label = False: voorspelt voor elk target met het MultiHead-model (uit "_multi").
        """
        if test_df is None:
            raise ValueError("Provided test set is empty. Please provide a non-empty test_df for prediction.")

        df_out = test_df.copy()
        # Voor elk target maken we kolom "Label_<t>"
        for t in self.targets:
            df_out[f"Label_{t}"] = pd.NA

        # CASE A: MultiHead
        if not getattr(self.train_cfg, "train_per_label", False):
            multi_model = self.models["_multi"]
            for t in self.targets:
                ds = _Dataset(
                    df_out,
                    [t],
                    getattr(self.pre_cfg, "context_labels", []),
                    input_size=self.train_cfg.input_size,
                )
                ld = DataLoader(ds, batch_size=self.train_cfg.batch_size,
                                shuffle=False, num_workers=0)

                all_preds: List[int] = []
                for x, proj, _ in ld:
                    x = x.to(self.device)
                    logits_dict = multi_model(x, proj.to(self.device) if proj.numel() else None)
                    logit = logits_dict[t].detach().cpu()
                    if self.out_dims[t] == 1:
                        probs = torch.sigmoid(logit.squeeze(1))
                        preds = (probs >= 0.5).long().numpy()
                    else:
                        preds = torch.argmax(torch.softmax(logit, dim=1), dim=1).numpy()
                    all_preds.extend(preds.tolist())

                nonnan_mask = df_out[t].notna()
                df_out.loc[nonnan_mask, f"Label_{t}"] = all_preds

        # CASE B: aparte modellen per target
        else:
            for t in self.targets:
                model = self.models[t]
                ds = _Dataset(
                    df_out,
                    [t],
                    getattr(self.pre_cfg, "context_labels", []),
                    input_size=self.train_cfg.input_size,
                )
                ld = DataLoader(ds, batch_size=self.train_cfg.batch_size,
                                shuffle=False, num_workers=0)

                all_preds: List[int] = []
                for x, proj, _ in ld:
                    x = x.to(self.device)
                    logits = model(x, proj.to(self.device) if proj.numel() else None).detach().cpu()
                    if self.out_dims[t] == 1:
                        probs = torch.sigmoid(logits.squeeze(1))
                        preds = (probs >= 0.5).long().numpy()
                    else:
                        preds = torch.argmax(torch.softmax(logits, dim=1), dim=1).numpy()
                    all_preds.extend(preds.tolist())

                nonnan_mask = df_out[t].notna()
                df_out.loc[nonnan_mask, f"Label_{t}"] = all_preds

        return df_out

    #  EVALUATE
    @torch.no_grad()
    def evaluate(
        self,
        predict_df: pd.DataFrame,
        plots: Union[str, List[str]] = None,
        metrics: List[str] = None,
    ) -> pd.DataFrame:
        """
        Verwacht predict_df met kolommen 'Label_<target>' voor elk target.
        • metrics: lijst van te berekenen metrics, bv. ["AUC", "accuracy", "F1"].
        • plots: (optioneel) 'confusion_matrix', 'loss_vs_epoch', 'lr_vs_epoch'
                 (String of list). Default: None (geen plots).
        Retourneert DataFrame met per target: de gevraagde metrics.
        """
        if predict_df is None:
            raise ValueError("Provided DataFrame for evaluation is empty. Please provide valid prediction results.")

        if isinstance(plots, str):
            plots = [plots]
        plots = plots or []

        if metrics is None:
            metrics = ["AUC", "accuracy"]

        records = []
        for t in self.targets:
            col_true = t
            col_pred = f"Label_{t}"
            row: Dict[str, Any] = {"target": t}

            if col_true not in predict_df.columns or col_pred not in predict_df.columns:
                for m in metrics:
                    row[m] = float("nan")
                records.append(row)
                continue

            df_sub = predict_df.dropna(subset=[col_true, col_pred]).copy()
            if df_sub.empty:
                for m in metrics:
                    row[m] = float("nan")
                records.append(row)
                continue

            y_true = df_sub[col_true].astype(int).to_numpy()
            y_pred = df_sub[col_pred].astype(int).to_numpy()

            # Bereken metrics
            for m in metrics:
                if m == "AUC":
                    if self.out_dims[t] == 1:
                        try:
                            val = roc_auc_score(y_true, y_pred.astype(float))
                        except ValueError:
                            val = float("nan")
                    else:
                        y_onehot = torch.nn.functional.one_hot(
                            torch.tensor(y_true), self.out_dims[t]
                        ).numpy()
                        preds_onehot = torch.nn.functional.one_hot(
                            torch.tensor(y_pred), self.out_dims[t]
                        ).numpy()
                        try:
                            val = roc_auc_score(y_onehot, preds_onehot, multi_class="ovo")
                        except ValueError:
                            val = float("nan")
                    row["AUC"] = val

                elif m == "accuracy":
                    row["accuracy"] = accuracy_score(y_true, y_pred)

                elif m == "F1":
                    if self.out_dims[t] == 1:
                        row["F1"] = f1_score(y_true, y_pred, zero_division=0)
                    else:
                        row["F1"] = f1_score(y_true, y_pred, average="macro", zero_division=0)

                else:
                    raise ValueError(f"Onbekende metric '{m}'")

            records.append(row)

        # Maak DataFrame met de berekende metrics
        results_df = pd.DataFrame(records)

        # Indien plots gevraagd, maak gecombineerde subplots per label
        if any(p in plots for p in ("confusion_matrix", "loss_vs_epoch", "lr_vs_epoch")):
            n_targets = len(self.targets)
            # Voor elk target: 3 kolommen (confusion, loss vs epoch, lr vs epoch)
            fig, axes = plt.subplots(
                n_targets, 3,
                figsize=(3 * 4, n_targets * 3),
                squeeze=False
            )

            for i, t in enumerate(self.targets):
                # 1) Confusion matrix
                if "confusion_matrix" in plots:
                    col_true = t
                    col_pred = f"Label_{t}"
                    df_sub = predict_df.dropna(subset=[col_true, col_pred]).copy()
                    if not df_sub.empty:
                        y_true = df_sub[col_true].astype(int).to_numpy()
                        y_pred = df_sub[col_pred].astype(int).to_numpy()
                        if self.out_dims[t] == 1:
                            cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
                            labels_plot = [0, 1]
                        else:
                            cm = confusion_matrix(
                                y_true, y_pred, labels=list(range(self.out_dims[t]))
                            )
                            labels_plot = list(range(self.out_dims[t]))
                    else:
                        cm = None
                        labels_plot = []

                    ax_cm = axes[i][0]
                    if cm is not None:
                        im = ax_cm.imshow(cm, cmap="Blues")
                        ax_cm.set_title(f"Confusion Matrix: {t}")
                        ax_cm.set_xlabel("Prediction Label")
                        ax_cm.set_ylabel("True Label")
                        ax_cm.set_xticks(range(len(labels_plot)))
                        ax_cm.set_yticks(range(len(labels_plot)))
                        for r in range(cm.shape[0]):
                            for c in range(cm.shape[1]):
                                ax_cm.text(c, r, int(cm[r, c]), ha="center", va="center", fontsize=8)
                    else:
                        ax_cm.axis("off")
                        ax_cm.set_title(f"Confusion Matrix: {t}\n(none)")
                else:
                    axes[i][0].axis("off")

                # 2) Loss vs epoch (train + val)
                if "loss_vs_epoch" in plots:
                    tr = self.train_loss_history.get(t, [])
                    val = self.val_loss_history.get(t, [])
                    epochs = list(range(1, max(len(tr), len(val)) + 1))

                    ax_loss = axes[i][1]
                    if tr:
                        ax_loss.plot(list(range(1, len(tr) + 1)), tr, label="train-loss")
                    if val:
                        ax_loss.plot(list(range(1, len(val) + 1)), val, linestyle="--", label="val-loss")
                    ax_loss.set_title(f"Train/Val Loss: {t}")
                    ax_loss.set_xlabel("Epoch")
                    ax_loss.set_ylabel("Loss")
                    ax_loss.legend()
                else:
                    axes[i][1].axis("off")

                # 3) LR vs epoch
                if "lr_vs_epoch" in plots:
                    # Omdat we geen scheduler meer gebruiken, is er per definitie geen lr_history
                    ax_lr = axes[i][2]
                    ax_lr.axis("off")
                    ax_lr.set_title(f"LR: {t}\n(none)")
                else:
                    axes[i][2].axis("off")

            plt.tight_layout()
            plt.show()
            plt.close(fig)

        return results_df

    #  SAVE / LOAD
    def save(self, file_path: str | Path) -> None:
        """
        Sla model(staten) op:
          • Als train_per_label=False: sla het MultiHead-model op onder 'multi_state'
          • Als train_per_label=True: sla per target een state_dict op onder 'models'
        """
        state: Dict[str, Any] = {"out_dims": self.out_dims}
        if "_multi" in self.models:
            multi_state = self.models["_multi"].state_dict()
            state["multi_state"] = multi_state
        else:
            state["models"] = {t: m.state_dict() for t, m in self.models.items()}
        torch.save(state, file_path)

    def load(self, file_path: str | Path) -> None:
        """
        Laad alle modellen. 
        - Voor MultiHead (train_per_label=False) wordt het model met 'multi_state' geload.
        - Anders: per target een SingleHead-model geladen uit state dicts.
        """
        ckpt = torch.load(file_path, map_location=self.device)
        self.out_dims = ckpt["out_dims"]

        # Context-cols voor reconstructie (meestal leeg bij load)
        context_cols: List[str] = []

        if "multi_state" in ckpt:
            # Herstel MultiHead-model
            bb_dummy, nf_dummy = backbone(self.train_cfg.pretrained_models[0], pretrained=False)
            multi_model = MultiHead(
                bb=bb_dummy,
                nf=nf_dummy,
                out_dims=self.out_dims,
                proj_dim=0,
                dropout_rate=(self.train_cfg.dropout_rate
                              if getattr(self.train_cfg, "dropout", False) else None),
            )
            multi_model.load_state_dict(ckpt["multi_state"])
            multi_model.to(self.device).eval()
            self.models["_multi"] = multi_model

        else:
            # Herstel één SingleHead per target
            for t, sd in ckpt["models"].items():
                out_dim = self.out_dims[t]
                bb_dummy, nf_dummy = backbone(self.train_cfg.pretrained_models[0], pretrained=False)
                model = SingleHead(
                    bb_dummy,
                    nf_dummy,
                    out_dim,
                    proj_dim=0,
                    dropout_rate=(self.train_cfg.dropout_rate
                                  if getattr(self.train_cfg, "dropout", False) else None),
                )
                model.load_state_dict(sd)
                model.to(self.device).eval()
                self.models[t] = model
