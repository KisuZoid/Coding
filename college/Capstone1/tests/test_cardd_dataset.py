"""Unit tests for the CarDD-COCO training adapter (Phase 2 prep).

Requires the dataset on disk (git-ignored). Tests skip cleanly when it is
absent, so this file never fails CI on a machine without the data.

The `ai` conda environment must be active (has torch + opencv):

    conda activate ai
    python -m pytest tests/test_cardd_dataset.py
"""

from __future__ import annotations

from pathlib import Path

import pytest
import torch

DATA_ROOT_REPO = Path(__file__).resolve().parents[1] / "datasets" / "CarDD_COCO"


@pytest.fixture(scope="module")
def data_root() -> Path:
    if not (DATA_ROOT_REPO / "annotations" / "instances_train2017.json").exists():
        pytest.skip("CarDD_COCO dataset not present on disk")
    return DATA_ROOT_REPO


def test_splits_are_disjoint(data_root: Path) -> None:
    from ml.training.cardd_dataset import CarddInstanceSegDataset

    seen: dict[int, str] = {}
    for split in ("train2017", "val2017", "test2017"):
        ds = CarddInstanceSegDataset(data_root, split=split)
        # Check a bounded sample of each split rather than decoding every image.
        for i in range(0, len(ds), 37):
            img_id = ds[i]["image_id"]
            assert img_id not in seen, f"image {img_id} leaked across splits"
            seen[img_id] = split


@pytest.mark.parametrize("split", ["train2017", "val2017", "test2017"])
def test_decodes_masks_and_labels(data_root: Path, split: str) -> None:
    from ml.training.cardd_dataset import CarddInstanceSegDataset

    ds = CarddInstanceSegDataset(data_root, split=split, limit=16)
    assert len(ds) > 0
    known = set(ds.category_ids())
    for i in range(len(ds)):
        item = ds[i]
        assert item["image"].shape == (3, 512, 512)
        assert item["image"].dtype == torch.float32
        assert 0.0 <= float(item["image"].min()) <= float(item["image"].max()) <= 1.0
        assert item["masks"].shape[1:] == (512, 512)
        assert item["masks"].dtype == torch.uint8
        assert set(int(lbl) for lbl in item["labels"].tolist()) <= known
        assert int(item["masks"].sum()) > 0
        assert int(item["masks"].max()) == 1


def test_masks_correspond_to_image(data_root: Path) -> None:
    from ml.training.cardd_dataset import CarddInstanceSegDataset

    ds = CarddInstanceSegDataset(data_root, split="val2017", limit=16)
    for i in range(len(ds)):
        item = ds[i]
        img_h, img_w = item["image"].shape[1:]
        assert item["masks"].shape[1:] == (img_h, img_w)
        for m in item["masks"]:
            assert m.max() in (0, 1)


def test_collate_pads_to_batch_max(data_root: Path) -> None:
    from ml.training.cardd_dataset import CarddInstanceSegDataset, collate_seg

    ds = CarddInstanceSegDataset(data_root, split="val2017", limit=16)
    batch = collate_seg([ds[i] for i in range(3)])
    max_instances = max(ds[i]["masks"].shape[0] for i in range(3))
    assert batch["image"].shape == (3, 3, 512, 512)
    assert batch["masks"].shape == (3, max_instances, 512, 512)
    assert batch["labels"].shape == (3, max_instances)
    assert batch["masks"].dtype == torch.uint8
