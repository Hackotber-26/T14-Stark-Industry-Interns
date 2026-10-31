from __future__ import annotations

import cv2
import numpy as np

from .config import (MIN_TEXTURE_CONTRAST, CHANGE_THRESHOLD, ROAD_LIKE_MIN, ROAD_LIKE_SCALE, GRABCUT_ITERS, MIN_DEFECT_CONTRAST,
                     MIN_DEFECT_FRAC_OF_ROI, QUALITY_GOOD, QUALITY_POOR,
                     REMAINING_DILATE_PX, RING_PX, TEXTURE_WEIGHT, TEXTURE_WIN)
from .types import CheckResult


def roi_to_mask(shape: tuple, roi_norm: list[list[float]]) -> np.ndarray:
    """Rasterize a normalized polygon in image coordinates."""
    h, w = shape[:2]
    points = np.rint(np.asarray(roi_norm) * [w, h]).astype(np.int32)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    return mask


def _road_ring(box: np.ndarray, valid: np.ndarray | None) -> np.ndarray:
    """Band of surrounding road just outside the marked box."""
    ring = cv2.subtract(cv2.dilate(box, np.ones((RING_PX, RING_PX), np.uint8)), box)
    return cv2.bitwise_and(ring, valid) if valid is not None else ring


def defect_mask(bgr: np.ndarray, roi_norm, valid: np.ndarray | None = None) -> np.ndarray:
    """Segment the damaged surface inside the marked box.

    GrabCut is seeded with the box interior as probable damage and everything
    outside the box as road. The result is rejected when the segmented region
    does not differ clearly in colour from the surrounding road. A robust
    colour/texture fallback recovers damage missed by GrabCut.
    """
    box = roi_to_mask(bgr.shape, roi_norm)
    if valid is not None:
        box = cv2.bitwise_and(box, valid)
    empty = np.zeros(box.shape, np.uint8)
    if np.count_nonzero(box) < 50:
        return empty
    x, y, w, h = cv2.boundingRect(box)
    height, width = box.shape
    pad = int(0.6 * max(w, h))
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(width, x + w + pad), min(height, y + h + pad)
    crop, crop_box = bgr[y0:y1, x0:x1], box[y0:y1, x0:x1]
    seeds = np.full(crop_box.shape, cv2.GC_BGD, np.uint8)
    seeds[crop_box > 0] = cv2.GC_PR_FGD
    core = cv2.erode(crop_box, np.ones((max(3, h // 5), max(3, w // 5)), np.uint8))
    seeds[(crop_box > 0) & (core == 0)] = cv2.GC_PR_BGD
    background, foreground = np.zeros((1, 65)), np.zeros((1, 65))
    try:
        cv2.setRNGSeed(0)
        cv2.grabCut(crop, seeds, None, background, foreground, GRABCUT_ITERS, cv2.GC_INIT_WITH_MASK)
    except cv2.error:
        seeds[:] = cv2.GC_BGD
    found = ((seeds == cv2.GC_FGD) | (seeds == cv2.GC_PR_FGD)).astype(np.uint8) * 255
    found = cv2.morphologyEx(found, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = empty.copy()
    mask[y0:y1, x0:x1] = found
    mask = cv2.bitwise_and(mask, box)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    if count > 1:
        largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        mask = np.where(labels == largest, 255, 0).astype(np.uint8)
    ring = _road_ring(box, valid)
    if not np.any(ring):
        return empty
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    road_colour = np.median(lab[ring > 0], axis=0)
    light_ = lab[..., 0]
    mean_ = cv2.blur(light_, (TEXTURE_WIN, TEXTURE_WIN))
    texture_ = np.sqrt(np.maximum(cv2.blur(light_ * light_, (TEXTURE_WIN, TEXTURE_WIN)) - mean_ * mean_, 0))
    road_texture = float(np.median(texture_[ring > 0]))

    def has_contrast(candidate: np.ndarray) -> bool:
        """Damage must differ from the road in colour OR in surface texture.

        Water-filled potholes often match the road colour but are much
        smoother (or rougher) than asphalt, so texture is checked too.
        """
        if not np.any(candidate):
            return False
        contrast = np.linalg.norm(np.median(lab[candidate > 0], axis=0) - road_colour)
        texture_change = abs(float(np.median(texture_[candidate > 0])) - road_texture) / (road_texture + 1.0)
        return bool(contrast >= MIN_DEFECT_CONTRAST or texture_change >= MIN_TEXTURE_CONTRAST)

    if has_contrast(mask):
        return mask

    # Estimate a robust distance in colour and local texture from nearby road.
    light = lab[..., 0]
    mean = cv2.blur(light, (TEXTURE_WIN, TEXTURE_WIN))
    variance = cv2.blur(light * light, (TEXTURE_WIN, TEXTURE_WIN)) - mean * mean
    features = np.dstack((lab, np.sqrt(np.maximum(variance, 0))))
    samples = features[ring > 0]
    median = np.median(samples, axis=0)
    mad = np.median(np.abs(samples - median), axis=0)
    z = np.abs(features - median) / (1.4826 * mad + 1e-3)
    distance = np.sqrt((np.sum(z[..., :3] ** 2, axis=2)
                        + TEXTURE_WEIGHT * z[..., 3] ** 2) / (3 + TEXTURE_WEIGHT))
    distance = cv2.GaussianBlur(distance, (5, 5), 1)
    threshold = np.percentile(distance[ring > 0], 93)
    fallback = ((distance > threshold) & (box > 0)).astype(np.uint8) * 255
    fallback = cv2.morphologyEx(fallback, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    fallback = cv2.morphologyEx(fallback, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    fallback = cv2.bitwise_and(fallback, box)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(fallback)
    mask = empty.copy()
    for label in range(1, count):
        if stats[label, cv2.CC_STAT_AREA] >= 0.03 * np.count_nonzero(box):
            mask[labels == label] = 255
    return mask if has_contrast(mask) else empty


def _remaining_damage(before_bgr, after_bgr, box, valid) -> np.ndarray:
    """Pixels that still look damaged in the aligned after photo.

    A pixel counts as repaired only if it changed since the before photo AND
    now looks like the surrounding road. Lighting is matched on the road ring
    first, so a brighter or darker photo does not count as a repair.
    """
    ring = _road_ring(box, valid) > 0
    before = cv2.cvtColor(cv2.GaussianBlur(before_bgr, (0, 0), 2), cv2.COLOR_BGR2LAB).astype(np.float32)
    after = cv2.cvtColor(cv2.GaussianBlur(after_bgr, (0, 0), 2), cv2.COLOR_BGR2LAB).astype(np.float32)
    if not np.any(ring):
        return np.ones(box.shape, bool)
    for c in range(3):
        mb, sb = before[..., c][ring].mean(), before[..., c][ring].std() + 1e-3
        ma, sa = after[..., c][ring].mean(), after[..., c][ring].std() + 1e-3
        after[..., c] = (after[..., c] - ma) / sa * sb + mb
    change = cv2.GaussianBlur(np.linalg.norm(after - before, axis=2), (0, 0), 3)
    road = np.median(before[ring], axis=0)
    road_dist = np.linalg.norm(before[ring] - road, axis=1)
    road_limit = max(ROAD_LIKE_MIN, float(np.percentile(road_dist, 95)) * ROAD_LIKE_SCALE)
    looks_like_road = cv2.GaussianBlur(np.linalg.norm(after - road, axis=2), (0, 0), 3) < road_limit
    return ~((change >= CHANGE_THRESHOLD) & looks_like_road)


def percent_resolved(before_bgr, after_aligned_bgr, roi_norm, valid_mask) -> tuple:
    """Return repaired percentage, areas, the before damage mask and the remaining-damage mask."""
    before = defect_mask(before_bgr, roi_norm)
    box = roi_to_mask(before_bgr.shape, roi_norm)
    valid = valid_mask if valid_mask is not None else np.full(box.shape, 255, np.uint8)
    area = int(np.count_nonzero(before))
    box_area = int(np.count_nonzero(box))
    if not box_area or not area or area / box_area < MIN_DEFECT_FRAC_OF_ROI:
        return None, area, 0, before, np.zeros_like(before)
    still_damaged = _remaining_damage(before_bgr, after_aligned_bgr, box, valid)
    after = ((before > 0) & still_damaged & (valid > 0)).astype(np.uint8) * 255
    remaining = int(np.count_nonzero(after))
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
    """Overlay damage, its original outline, and a readable colour legend."""
    result = before_bgr.copy()
    dilated = cv2.dilate(after_mask_aligned, np.ones((REMAINING_DILATE_PX, REMAINING_DILATE_PX), np.uint8))
    repaired = (before_mask > 0) & (dilated == 0)
    remaining = (before_mask > 0) & (after_mask_aligned > 0)
    for selected, colour in ((repaired, (94, 197, 34)), (remaining, (68, 68, 239))):
        result[selected] = (0.55 * before_bgr[selected] + 0.45 * np.array(colour)).astype(np.uint8)
        contours, _ = cv2.findContours(selected.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(result, contours, -1, colour, 2)
    contours, _ = cv2.findContours(before_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(result, contours, -1, (255, 255, 255), 1)

    h, w = result.shape[:2]
    scale = min(1.0, w / 360, h / 80)
    strip_h = max(1, min(h, round(42 * scale)))
    top = h - strip_h
    strip = result[top:].copy()
    strip[:] = (20, 20, 20)
    result[top:] = cv2.addWeighted(strip, 0.70, result[top:], 0.30, 0)
    for fraction, label, colour in ((0.04, 'Repaired', (94, 197, 34)),
                                    (0.50, 'Still broken', (68, 68, 239))):
        x = round(w * fraction)
        y = top + round(12 * scale)
        side = max(1, round(15 * scale))
        cv2.rectangle(result, (x, y), (x + side, y + side), colour, -1)
        cv2.putText(result, label, (x + side + round(8 * scale), y + side),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55 * scale, (255, 255, 255),
                    1, cv2.LINE_AA)
    return result
