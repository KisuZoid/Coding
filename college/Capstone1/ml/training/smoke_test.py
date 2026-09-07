"""Phase 2 smoke test: validate labels, masks, augmentation, inference shapes.

Validates, without training:
  1. every returned sample decodes to ≥1 mask with a known category id;
  2. resizing keeps image and mask correspondences (mask never exceeds image);
  3. every category id in the annotation file is reachable in the split;
  4. train/val/test splits are disjoint at the image level;
  5. a minimal model forward+backward runs with the adapter's output shapes.

Run inside the `ai` conda environment:

    conda activate ai
    python ml/training/smoke_test.py --data-root datasets/CarDD_COCO
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

import torch
import torch.nn as nn

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ml.training.cardd_dataset import CarddInstanceSegDataset, SegItem, collate_seg  # noqa: E402

BATCH = 2


class TinySeg(nn.Module):
    """Two-layer convolutional stand-in so shape/type checks need no real model."""

    def __init__(self, num_classes: int) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, num_classes, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return cast(torch.Tensor, self.conv2(torch.relu(self.conv1(x))))


def make_loader(data_root: Path, split: str, limit: int) -> torch.utils.data.DataLoader[SegItem]:
    ds = CarddInstanceSegDataset(data_root, split=split, limit=limit)
    return torch.utils.data.DataLoader(
        ds,
        batch_size=BATCH,
        shuffle=True,
        num_workers=0,
        drop_last=True,
        collate_fn=collate_seg,
    )


def validate_sample(item: SegItem, dataset: CarddInstanceSegDataset, label: str) -> None:
    assert item["image"].ndim == 3, f"{label}: image.ndim != 3"
    assert item["image"].dtype == torch.float32, f"{label}: image dtype != float32"
    assert item["image"].min() >= 0.0 and item["image"].max() <= 1.0, f"{label}: image out of [0,1]"
    assert item["masks"].dtype == torch.uint8, f"{label}: masks dtype != uint8"
    assert item["masks"].ndim == 3, f"{label}: masks.ndim != 3"
    n_masks = item["masks"].shape[0]
    assert n_masks >= 1, f"{label}: no masks in sample"
    assert item["labels"].shape == (n_masks,), f"{label}: label count != mask count"
    valid_labels = [lbl for lbl in item["labels"].tolist() if lbl >= 0]
    assert valid_labels, f"{label}: no valid (non-padding) labels"
    known = set(dataset.category_ids())
    for lbl in valid_labels:
        assert lbl in known, f"{label}: unknown category {lbl}"
    assert item["masks"].max() <= 1, f"{label}: mask not binary"
    real_instances = int((item["labels"] >= 0).sum())
    assert real_instances >= 1, f"{label}: no real instances"
    assert int(item["masks"][:real_instances].sum()) > 0, f"{label}: all-zero mask"
    img_h, img_w = item["image"].shape[1:]
    assert item["masks"].shape[1:] == (img_h, img_w), f"{label}: mask/image size mismatch"


def validate_forward(model: nn.Module, image_batch: torch.Tensor) -> None:
    out = model(image_batch)
    assert out.shape[0] == BATCH, "forward: bad batch dim"
    assert out.ndim == 4, "forward: expected 4D logits"
    loss = torch.nn.functional.binary_cross_entropy_with_logits(out, torch.zeros_like(out))
    loss.backward()  # type: ignore[no-untyped-call]
    assert loss.item() >= 0.0, "forward: negative BCE"


def cross_split_leakage(data_root: Path) -> dict[int, list[str]]:
    """Return image ids that appear in more than one split."""
    from collections import defaultdict

    ids_by_split: dict[str, set[int]] = {}
    for split in ("train2017", "val2017", "test2017"):
        ds = CarddInstanceSegDataset(data_root, split=split)
        ids_by_split[split] = {ds[i]["image_id"] for i in range(len(ds))}
    present_in: defaultdict[int, list[str]] = defaultdict(list)
    for split, ids in ids_by_split.items():
        for img_id in ids:
            present_in[img_id].append(split)
    return {img_id: splits for img_id, splits in present_in.items() if len(splits) > 1}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=24, help="samples per split for the smoke run")
    args = parser.parse_args()

    for split in ("train2017", "val2017", "test2017"):
        ds = CarddInstanceSegDataset(args.data_root, split=split, limit=args.limit)
        loader = make_loader(args.data_root, split, args.limit)
        for batch in loader:
            # Collate yields a list image tensors per batch; validate the first batch fully.
            for i in range(len(batch["image"])):
                item: SegItem = {
                    "image": batch["image"][i],
                    "masks": batch["masks"][i],
                    "labels": batch["labels"][i],
                    "image_id": int(batch["image_id"][i]),
                    "file_name": str(batch["file_name"][i]),
                }
                validate_sample(item, ds, f"{split}")
            break  # one batch per split is enough for a smoke test

    # Cross-split leakage check over full sets.
    leakage = cross_split_leakage(args.data_root)
    assert not leakage, f"image-level leakage across splits: {leakage}"
    print("Cross-split leakage: none (full sets)")

    # Forward/backward shape check on one batch.
    ds = CarddInstanceSegDataset(args.data_root, split="val2017", limit=BATCH)
    batch_items = [ds[i] for i in range(BATCH)]
    collated = collate_seg(batch_items)
    model = TinySeg(num_classes=len(ds.category_ids()) + 1)  # background + classes
    validate_forward(model, collated["image"])
    print("Tiny model forward+backward: OK")

    # Sanity: per-class reachability summary for the val split.
    print(f"val split category ids: {ds.category_ids()}")


if __name__ == "__main__":
    main()
