"""Unit tests for the CarDD data adapter (Phase 2).

Requires the dataset on disk (git-ignored). Tests skip cleanly when it is
absent, so this file never fails CI on a machine without the data.

The `ai` conda environment must be active (has torch + opencv):

    conda activate ai
    python -m pytest tests/test_cardd_adapter.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

DATA_ROOT_REPO = Path(__file__).resolve().parents[1] / "datasets" / "CarDD_COCO"


@pytest.fixture(scope="module")
def data_root() -> Path:
    if not (DATA_ROOT_REPO / "annotations" / "instances_train2017.json").exists():
        pytest.skip("CarDD_COCO dataset not present on disk")
    return DATA_ROOT_REPO


def test_rejects_unknown_split(data_root: Path) -> None:
    from ml.datasets.cardd_adapter import CarddAdapter

    with pytest.raises(ValueError):
        CarddAdapter(data_root, "unsplit")


def test_categories_and_ids(data_root: Path) -> None:
    from ml.datasets.cardd_adapter import CarddAdapter

    adapter = CarddAdapter(data_root, "train2017")
    ids = adapter.category_ids()
    assert ids == list(range(1, 7)), f"category ids {ids}"
    names = {c.name for c in adapter.categories()}
    assert names == {
        "dent",
        "scratch",
        "crack",
        "glass shatter",
        "lamp broken",
        "tire flat",
    }


def test_splits_are_disjoint_and_populated(data_root: Path) -> None:
    from ml.datasets.cardd_adapter import CarddAdapter

    seen_ids: dict[int, str] = {}
    seen_files: dict[str, str] = {}
    for split in ("train2017", "val2017", "test2017"):
        adapter = CarddAdapter(data_root, split)
        images = adapter.images()
        assert len(images) > 0, split
        for img in images:
            assert img.image_id not in seen_ids, f"{split}: image id leaked"
            assert img.file_name not in seen_files, f"{split}: file name leaked"
            seen_ids[img.image_id] = split
            seen_files[img.file_name] = split


def test_rasterize_return_shape(data_root: Path) -> None:
    from ml.datasets.cardd_adapter import CarddAdapter

    adapter = CarddAdapter(data_root, "val2017")
    images = adapter.images()
    colored = [img for img in images if img.annotations]
    assert colored, "val2017 has no annotated images"
    sample = colored[0]
    masks = adapter.rasterize(sample)
    assert masks.shape == (len(sample.annotations), sample.height, sample.width)
    assert masks.dtype == np.uint8
    assert int(masks.max()) == 1


def test_load_image_rgb(data_root: Path) -> None:
    from ml.datasets.cardd_adapter import CarddAdapter

    adapter = CarddAdapter(data_root, "val2017")
    sample = adapter.images()[0]
    img = adapter.load_image(sample)
    assert img.shape[2] == 3
    assert img.max() > 0, "image decoded but all black"
