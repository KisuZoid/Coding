"""CarDD-COCO training dataset adapter for PyTorch (Phase 2).

Consumes :class:`ml.datasets.cardd_adapter.CarddAdapter` for metadata,
annotations, image loading, and mask rasterization, then applies resize and
normalization for training. Loading of image bytes stays lazy (per-sample),
and the dataset is split-scoped so train/val/test never mix.

Run inside the `ai` conda environment.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

from ml.datasets.cardd_adapter import CarddAdapter, CarddImage

TARGET_SIZE = 512


class SegItem(TypedDict):
    image: torch.Tensor  # float32, 3xHxW in [0, 1]
    masks: torch.Tensor  # uint8,  NxHxW
    labels: torch.Tensor  # int64, N category ids
    image_id: int
    file_name: str


class CarddInstanceSegDataset(Dataset[SegItem]):
    """PyTorch Dataset for CarDD-COCO instance segmentation."""

    def __init__(
        self,
        data_root: Path | str,
        split: str,
        target_size: int = TARGET_SIZE,
        allow_empty: bool = False,
        limit: int | None = None,
        seed: int = 0,
        augment: bool = False,
    ) -> None:
        self._adapter = CarddAdapter(data_root, split)
        self._target_size = target_size
        self._use_augment = augment
        entries = self._adapter.images()
        if not allow_empty:
            entries = [e for e in entries if e.annotations]
        self._entries = sorted(entries, key=lambda e: e.image_id)
        if limit is not None:
            rng = np.random.default_rng(seed)
            idx = rng.choice(len(self._entries), size=min(limit, len(self._entries)), replace=False)
            self._entries = [self._entries[int(i)] for i in idx]
            self._entries.sort(key=lambda e: e.image_id)

    def __len__(self) -> int:
        return len(self._entries)

    def _resize(self, img: np.ndarray, masks: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Resize image and masks together so correspondences are preserved."""
        if img.shape[0] == self._target_size and img.shape[1] == self._target_size:
            return img, masks
        target = (self._target_size, self._target_size)
        resized_img = cv2.resize(img, target, interpolation=cv2.INTER_LINEAR)
        resized_masks = np.zeros(
            (masks.shape[0], self._target_size, self._target_size), dtype=np.uint8
        )
        for i in range(masks.shape[0]):
            resized_masks[i] = cv2.resize(masks[i], target, interpolation=cv2.INTER_NEAREST)
        return resized_img, resized_masks

    @staticmethod
    def _augment(img: torch.Tensor, masks: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Light train-time augmentation, applied identically to image and masks.

        Random horizontal flip (image and masks together, so pixel
        correspondences are preserved) plus a mild brightness/contrast jitter
        on the image only. Uses the global torch RNG so that seeding
        deterministic runs works and flips vary across epochs.
        """
        if torch.rand(1).item() < 0.5:
            img = torch.flip(img, dims=[2])
            masks = torch.flip(masks, dims=[2])
        contrast = 1.0 + 0.1 * (torch.rand(1).item() - 0.5)
        brightness = 0.05 * (torch.rand(1).item() - 0.5)
        img = torch.clamp(img * contrast + brightness, 0.0, 1.0)
        return img, masks

    def __getitem__(self, index: int) -> SegItem:
        entry: CarddImage = self._entries[index]
        img = self._adapter.load_image(entry)
        masks = self._adapter.rasterize(entry)
        labels = np.array([a.category_id for a in entry.annotations], dtype=np.int64)

        img, masks = self._resize(img, masks)
        img_normalized = img.astype(np.float32) / 255.0
        img_t = torch.from_numpy(np.transpose(img_normalized, (2, 0, 1))).contiguous()
        masks_t = torch.from_numpy(masks).to(torch.uint8)
        if self._use_augment:
            img_t, masks_t = self._augment(img_t, masks_t)
        labels_t = torch.from_numpy(labels).to(torch.int64)

        return {
            "image": img_t,
            "masks": masks_t,
            "labels": labels_t,
            "image_id": entry.image_id,
            "file_name": entry.file_name,
        }

    def category_ids(self) -> list[int]:
        """Return the sorted category ids present in this split."""
        return self._adapter.category_ids()


def collate_seg(batch: list[SegItem]) -> dict[str, Any]:
    """Stack a batch, padding instance masks/labels to the batch's max instance count.

    Images share one target resolution; instance counts vary per image. We pad
    with empty masks and label -1 so the batch is rectangular, mirroring common
    instance-segmentation collation.
    """
    images = torch.stack([item["image"] for item in batch])
    max_instances = max(item["masks"].shape[0] for item in batch)
    img_h, img_w = images.shape[2:]
    masks_padded = torch.zeros((len(batch), max_instances, img_h, img_w), dtype=torch.uint8)
    labels_padded = torch.full((len(batch), max_instances), fill_value=-1, dtype=torch.long)
    for i, item in enumerate(batch):
        n = item["masks"].shape[0]
        masks_padded[i, :n] = item["masks"]
        labels_padded[i, :n] = item["labels"]
    return {
        "image": images,
        "masks": masks_padded,
        "labels": labels_padded,
        "image_id": torch.tensor([item["image_id"] for item in batch]),
        "file_name": [item["file_name"] for item in batch],
    }
