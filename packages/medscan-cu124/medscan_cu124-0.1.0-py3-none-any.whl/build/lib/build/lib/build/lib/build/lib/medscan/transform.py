import random
from pathlib import Path
from typing import Optional

import pandas as pd
import torch
from torchvision import io
import torchvision.transforms.functional as TF
from torchvision.utils import save_image

from .config import PreprocessConfig
def elastic_transform(image: torch.Tensor, alpha: float = 34.0, sigma: float = 4.0) -> torch.Tensor:
    from scipy.ndimage import gaussian_filter, map_coordinates
    import numpy as np

    image_np = image.numpy()
    shape = image_np.shape[1:]

    dx = gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma) * alpha
    dy = gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma) * alpha

    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))

    transformed = np.empty_like(image_np)
    for i in range(image_np.shape[0]):
        transformed[i] = map_coordinates(image_np[i], indices, order=1, mode='reflect').reshape(shape)

    return torch.tensor(transformed)

def _apply_augment(t: torch.Tensor, method: str, rng: random.Random, cfg: PreprocessConfig) -> torch.Tensor:
    out = t.clone()
    if method == "contrast":
        factor = rng.uniform(cfg.contrast_min, cfg.contrast_max)
        out = TF.adjust_contrast(out, factor)
    elif method == "elastic":
        out = elastic_transform(out, alpha=cfg.elastic_alpha, sigma=cfg.elastic_sigma)
    elif method == "contrast_elastic":
        factor = rng.uniform(cfg.contrast_min, cfg.contrast_max)
        out = TF.adjust_contrast(out, factor)
        out = elastic_transform(out, alpha=cfg.elastic_alpha, sigma=cfg.elastic_sigma)
    return out



def augment_and_balance(
    df_in: pd.DataFrame,
    config: PreprocessConfig,
    target_col: str,
    output_dir: str,
    seed: int = 42,
    img_column: str = "img_path"
) -> pd.DataFrame:
    """
    Past balancing en augmentatie toe op basis van PreprocessConfig
    """
    if not config.augment and not config.balance_on:
        return df_in.copy()

    rng = random.Random(seed)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Balancing
    df_bal = df_in.copy()
    if config.balance_on:
        counts = df_in[target_col].value_counts().to_dict()
        max_count = max(counts.values())
        for cls, cur in counts.items():
            need = max_count - cur
            pool = df_in[df_in[target_col] == cls]
            extra_rows = pool.sample(n=need, replace=True, random_state=seed)
            df_bal = pd.concat([df_bal, extra_rows], ignore_index=True)
        print(f"{target_col} – gebalanceerd: {dict(df_bal[target_col].value_counts())}")

    # Augmentatie
    new_rows = []
    for i, row in df_bal.iterrows():
        pid, sid = int(row["Patient_ID"]), int(row["Series_ID"])
        base = f"R{pid:04d}_S{sid}_{i}"
        img_path = row[img_column]
        rgb = io.read_image(img_path, io.ImageReadMode.RGB).float() / 255.

        # originele afbeelding opslaan
        orig_fname = output_dir / f"{base}_orig.png"
        save_image(rgb, orig_fname)
        r = row.to_dict(); r[img_column] = str(orig_fname)
        new_rows.append(r)

        if config.augment:
            for j in range(config.augment_factor):
                method = rng.choice(config.augment_methods)
                aug_t = _apply_augment(rgb, method, rng, config)
                fname = output_dir / f"{base}_{method}_{j}.png"
                save_image(aug_t, fname)
                r_aug = row.to_dict(); r_aug[img_column] = str(fname)
                new_rows.append(r_aug)

    df_augmented = pd.DataFrame(new_rows)
    return df_augmented
