"""Class-map contract tests (Phase D). Verbatim from CarDD-COCO categories."""

from __future__ import annotations

import pytest

from ml.inference.classes import (
    BACKGROUND_CLASS,
    CLASS_TO_ID,
    DAMAGE_CLASS_IDS,
    ID_TO_CLASS,
    NUM_CLASSES,
    validate_class_ids,
)


def test_car_dd_class_map_is_verbatim() -> None:
    assert ID_TO_CLASS == {
        0: "background",
        1: "dent",
        2: "scratch",
        3: "crack",
        4: "glass shatter",
        5: "lamp broken",
        6: "tire flat",
    }
    assert CLASS_TO_ID["tire flat"] == 6
    assert NUM_CLASSES == 7
    assert BACKGROUND_CLASS == 0
    assert DAMAGE_CLASS_IDS == (1, 2, 3, 4, 5, 6)


def test_validate_class_ids_rejects_unknown() -> None:
    validate_class_ids([1, 2, 3])
    with pytest.raises(ValueError):
        validate_class_ids([1, 99])
