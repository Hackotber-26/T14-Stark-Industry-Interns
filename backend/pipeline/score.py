from __future__ import annotations

import cv2
import numpy as np

from .config import (ANOMALY_Z, MIN_DEFECT_FRAC_OF_ROI, QUALITY_GOOD,
                     QUALITY_POOR, REMAINING_DILATE_PX, RING_PX,
                     TEXTURE_WEIGHT, TEXTURE_WIN)
from .types import CheckResult


def roi_to_mask(shape: tuple, roi_norm: list[list[float]]) -> np.ndarray:
    """Rasterize a normalized polygon in image coordinates."""
    h, w = shape[:2]
    points = np.rint(np.asarray(roi_norm) * [w, h]).astype(np.int32)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    return mask


def defect_mask(bgr: np.ndarray, roi_norm, valid: np.ndarray | None = None) -> np.ndarray:
    """Measure colour and texture anomalies relative to this image's road ring."""
    box = roi_to_mask(bgr.shape, roi_norm)
    ring = cv2.subtract(cv2.dilate(box, np.ones((RING_PX, RING_PX), np.uint8)), box)
    if valid is not None:
        box = cv2.bitwise_and(box, valid)
        ring = cv2.bitwise_and(ring, valid)
    empty = np.zeros(box.shape, np.uint8)
    if not np.any(ring) or not np.any(box):
        return empty
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    light = lab[..., 0]
    mean = cv2.blur(light, (TEXTURE_WIN, TEXTURE_WIN))
    variance = cv2.blur(light * light, (TEXTURE_WIN, TEXTURE_WIN)) - mean * mean
    texture = np.sqrt(np.maximum(variance, 0))
    features = np.dstack((lab, texture))
    samples = features[ring > 0]
    median = np.median(samples, axis=0)
    mad = np.median(np.abs(samples - median), axis=0)
    z = np.abs(features - median) / (1.4826 * mad + 1e-3)
    anomaly = np.sqrt((np.sum(z[..., :3] ** 2, axis=2)
                       + TEXTURE_WEIGHT * z[..., 3] ** 2) / (3 + TEXTURE_WEIGHT))
    mask = ((anomaly > ANOMALY_Z) & (box > 0)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    mask = cv2.bitwise_and(mask, box)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    for label in range(1, count):
        if stats[label, cv2.CC_STAT_AREA] >= 0.02 * np.count_nonzero(box):
            empty[labels == label] = 255
    return empty


def percent_resolved(before_bgr, after_aligned_bgr, roi_norm, valid_mask) -> tuple:
    """Return repaired percentage, areas, and both measured defect masks."""
    before = defect_mask(before_bgr, roi_norm)
    after = defect_mask(after_aligned_bgr, roi_norm, valid_mask)
    area = int(np.count_nonzero(before))
    box_area = np.count_nonzero(roi_to_mask(before_bgr.shape, roi_norm))
    nearby = cv2.dilate(before, np.ones((REMAINING_DILATE_PX, REMAINING_DILATE_PX), np.uint8))
    remaining = min(area, int(np.count_nonzero(cv2.bitwise_and(after, nearby))))
    if not box_area or not area or area / box_area < MIN_DEFECT_FRAC_OF_ROI:
        return None, area, remaining, before, after
    pct = round(float(np.clip(100 * (1 - remaining / area), 0, 100)), 1)
    return pct, area, remaining, before, after


def patch_quality(after_aligned_bgr, before_mask) -> CheckResult:
    """Compare patch brightness and sharpness with the adjacent road."""
    ring = cv2.subtract(cv2.dilate(before_mask, np.ones((25, 25), np.uint8)),
                        cv2.dilate(before_mask, np.ones((5, 5), np.uint8)))
    region = before_mask > 0
    outside = ring > 0
    if not np.any(region) or not np.any(outside):
        return CheckResult('skipped', 'Not enough patch or surrounding road to assess quality')
    gray = cv2.cvtColor(after_aligned_bgr, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    mean_difference = abs(float(gray[region].mean()) - float(gray[outside].mean()))
    lap_ring = float(lap[outside].var())
    lap_difference = abs(float(lap[region].var()) - lap_ring)
    value = float(1 - np.clip(0.5 * mean_difference / 60
                              + 0.5 * lap_difference / max(lap_ring, 1), 0, 1))
    status = 'pass' if value >= QUALITY_GOOD else 'warn' if value >= QUALITY_POOR else 'fail'
    details = {'pass': 'Patch surface matches the surrounding road',
               'warn': 'Patch surface looks uneven', 'fail': 'Patch quality looks poor'}
    return CheckResult(status, details[status], score=value)


def heatmap(before_bgr, before_mask, after_mask_aligned) -> np.ndarray:
    """Overlay repaired and remaining defect pixels on the before image."""
    result = before_bgr.copy()
    dilated = cv2.dilate(after_mask_aligned, np.ones((REMAINING_DILATE_PX, REMAINING_DILATE_PX), np.uint8))
    repaired = (before_mask > 0) & (dilated == 0)
    remaining = (before_mask > 0) & (after_mask_aligned > 0)
    for selected, colour in ((repaired, (94, 197, 34)), (remaining, (68, 68, 239))):
        result[selected] = (0.55 * before_bgr[selected] + 0.45 * np.array(colour)).astype(np.uint8)
        contours, _ = cv2.findContours(selected.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(result, contours, -1, colour, 2)
    return result
