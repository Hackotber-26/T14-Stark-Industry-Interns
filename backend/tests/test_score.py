"""Synthetic road measurements against the SPEC section 7 contracts."""

import cv2
import numpy as np
import pytest

from backend.pipeline.score import defect_mask, percent_resolved
from backend.pipeline.segment import DefectDetector


@pytest.fixture
def road_case() -> tuple:
    """Build reproducible road and pothole textures without external assets."""
    rng = np.random.default_rng(0)
    shape = (480, 640)
    road_gray = np.clip(rng.normal(150, 4, shape), 0, 255).astype(np.uint8)
    road = np.repeat(road_gray[..., None], 3, axis=2)
    ellipse = np.zeros(shape, dtype=np.uint8)
    cv2.ellipse(ellipse, (320, 240), (110, 80), 0, 0, 360, 255, -1)
    hole_gray = np.clip(rng.normal(45, 7, shape), 0, 255).astype(np.uint8)
    hole = np.repeat(hole_gray[..., None], 3, axis=2)
    before = road.copy()
    before[ellipse > 0] = hole[ellipse > 0]
    roi = [[180 / 640, 130 / 480], [460 / 640, 130 / 480],
           [460 / 640, 350 / 480], [180 / 640, 350 / 480]]
    valid = np.full(shape, 255, dtype=np.uint8)
    return road, before, ellipse, roi, valid


def test_defect_mask_covers_ellipse_with_little_spill(road_case: tuple) -> None:
    _, before, ellipse, roi, _ = road_case
    mask = defect_mask(before, roi)
    assert mask.shape == ellipse.shape
    assert mask.dtype == np.uint8
    assert set(np.unique(mask)) <= {0, 255}
    inside = np.count_nonzero((mask > 0) & (ellipse > 0))
    outside = np.count_nonzero((mask > 0) & (ellipse == 0))
    assert inside / np.count_nonzero(ellipse) >= 0.70
    assert outside / np.count_nonzero(ellipse) <= 0.10


@pytest.mark.parametrize("repair", ["unchanged", "complete", "left_half", "darker"])
def test_percent_resolved_synthetic_repairs(road_case: tuple, repair: str) -> None:
    road, before, ellipse, roi, valid = road_case
    after = before.copy()
    if repair == "complete":
        after = road.copy()
    elif repair == "left_half":
        left = (ellipse > 0) & (np.indices(ellipse.shape)[1] < 320)
        after[left] = road[left]
    elif repair == "darker":
        after = (after.astype(np.float32) * 0.8).astype(np.uint8)
    pct, before_area, remaining_area, before_mask, after_mask = percent_resolved(
        before, after, roi, valid
    )
    assert pct is not None
    assert 0 <= pct <= 100
    assert pct == round(pct, 1)
    assert before_area == np.count_nonzero(before_mask)
    assert 0 <= remaining_area <= before_area
    for mask in (before_mask, after_mask):
        assert mask.shape == ellipse.shape
        assert mask.dtype == np.uint8
        assert set(np.unique(mask)) <= {0, 255}
    if repair == "complete":
        assert pct >= 90
    elif repair == "left_half":
        assert 35 <= pct <= 65
    else:
        assert pct <= 10


def test_plain_road_needs_review(road_case: tuple) -> None:
    road, _, _, roi, valid = road_case
    pct, *_ = percent_resolved(road, road.copy(), roi, valid)
    assert pct is None


def test_mock_detector_returns_no_suggestion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FIXCHECK_MOCK_SEG", "1")
    detector = DefectDetector(weights_path="/nonexistent/never-load.pt", device="cpu")
    assert detector.suggest_roi(np.zeros((480, 640, 3), dtype=np.uint8)) == (None, 0.0)
