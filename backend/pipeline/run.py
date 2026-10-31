"""Coordinate verification without coupling pipeline modules to HTTP."""
from datetime import datetime, timezone
import logging
import os
from pathlib import Path
from time import perf_counter
import cv2
import numpy as np
from . import align, config, dedupe, exif, match, score, segment, verdict, explain
from .types import LatLon, ScoreResult, CheckResult, to_dict


def ai_enabled() -> bool:
    """Read both advisory switches without requiring the optional model module."""
    return config.AI_SECOND_OPINION and os.getenv('FIXCHECK_NO_AI') != '1'


def auto_change_roi(before_bgr: np.ndarray, after_aligned_bgr: np.ndarray,
                    valid_mask: np.ndarray) -> list[list[float]] | None:
    """Find the largest substantial change after global lighting correction."""
    valid = valid_mask > 0
    if not np.any(valid):
        return None
    before = cv2.cvtColor(before_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    after = cv2.cvtColor(after_aligned_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    for channel in range(3):
        reference = before[...,channel][valid]
        sample = after[...,channel][valid]
        spread = float(sample.std())
        scale = float(reference.std()) / spread if spread > 1e-3 else 1.0
        after[...,channel] = (after[...,channel] - sample.mean()) * scale + reference.mean()
    difference = np.linalg.norm(after-before, axis=2)
    difference[~valid] = 0
    size = config.AUTO_CHANGE_BLUR
    difference = cv2.GaussianBlur(difference, (size,size), 0)
    threshold = max(float(np.percentile(difference[valid],config.AUTO_CHANGE_PERCENTILE)),
                    config.CHANGE_THRESHOLD * config.AUTO_CHANGE_THRESHOLD_SCALE)
    changed = ((difference > threshold) & valid).astype(np.uint8) * 255
    changed = cv2.morphologyEx(changed,cv2.MORPH_OPEN,
                               np.ones((config.AUTO_CHANGE_OPEN,config.AUTO_CHANGE_OPEN),np.uint8))
    changed = cv2.morphologyEx(changed,cv2.MORPH_CLOSE,
                               np.ones((config.AUTO_CHANGE_CLOSE,config.AUTO_CHANGE_CLOSE),np.uint8))
    changed[~valid] = 0
    count, _, stats, _ = cv2.connectedComponentsWithStats(changed)
    if count <= 1:
        return None
    component = stats[1 + int(np.argmax(stats[1:,cv2.CC_STAT_AREA]))]
    h, w = valid.shape
    x, y, width, height, area = map(int,component)
    if area < config.AUTO_CHANGE_MIN_FRAC * h * w:
        return None
    pad_x, pad_y = width * config.AUTO_CHANGE_PAD, height * config.AUTO_CHANGE_PAD
    x0, y0 = max(0.,x-pad_x)/w, max(0.,y-pad_y)/h
    x1, y1 = min(float(w),x+width+pad_x)/w, min(float(h),y+height+pad_y)/h
    return [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]


def verify(before_path: str, after_path: str, complaint_id: str,
           before_ll: LatLon | None, after_ll: LatLon | None,
           roi: list | None, known_hashes: list[tuple[str, str]],
           out_dir: str) -> dict:
    """Run evidence checks, measure the defect, and write result images."""
    start = perf_counter()
    timings = {}
    def timed(name, function, *args):
        tick = perf_counter()
        result = function(*args)
        timings[name] = round((perf_counter()-tick)*1000, 2)
        return result

    before = exif.read_bgr(before_path)
    after = exif.read_bgr(after_path)
    before = align.resize_max_side(before)
    after = align.resize_max_side(after)
    before_ll = before_ll if before_ll is not None else exif.read_gps(before_path)
    after_ll = after_ll if after_ll is not None else exif.read_gps(after_path)
    location = timed('location', match.gps_check, before_ll, after_ll)
    duplicate = timed('duplicate', dedupe.find_duplicate, dedupe.phash_hex(after), known_hashes, complaint_id)
    scene = timed('scene', match.scene_match, before, after)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_id = out.name
    def write(name, image):
        if not cv2.imwrite(str(out / f'{name}.jpg'), image):
            raise OSError(f'Could not save {name} image')
        return f'/files/{run_id}/{name}.jpg'
    images = {'before': write('before', before), 'after': write('after', after), 'after_aligned': None, 'heatmap': None}
    pct = None
    measurement = None
    roi_source = 'marked' if roi is not None else 'none'
    no_change = False
    quality = CheckResult('skipped', 'Not scored – photos do not match')
    if scene.check.status == 'pass':
        aligned = timed('align', align.warp_after_to_before, after, scene.H, before.shape)
        valid = align.valid_region_mask(after.shape, scene.H, before.shape)
        if roi is None:
            roi, _ = timed('detect', segment.get_detector().suggest_roi, before)
            if roi is not None:
                roi_source = 'model'
        if roi is None:
            roi = timed('auto_change', auto_change_roi, before, aligned, valid)
            if roi is not None:
                roi_source = 'auto_change'
        images['after_aligned'] = write('after_aligned', aligned)
        if roi is None:
            no_change = True
            pct = 0.0
            quality = CheckResult('skipped', 'Not scored – no changed region found')
            measurement = ScoreResult(pct, 0, 0, quality)
        else:
            pct, before_area, remaining_area, before_mask, after_mask = timed('score', score.percent_resolved, before, aligned, roi, valid)
            quality = score.patch_quality(aligned, before_mask)
            measurement = ScoreResult(pct, before_area, remaining_area, quality)
            images['heatmap'] = write('heatmap', score.heatmap(before, before_mask, after_mask))
    decision = timed('verdict', verdict.decide, location, duplicate, scene.check, measurement)
    if no_change and decision.verdict == 'NOT_FIXED':
        decision.reasons = ['No change detected between the photos; the reported problem appears untouched']
    explanation = timed('explain', explain.explain, decision, pct)
    ai_opinion = None
    if scene.check.status == 'pass' and roi is not None and ai_enabled():
        try:
            from .ai_check import ai_second_opinion
            opinion = timed('ai_second_opinion', ai_second_opinion, before, aligned, roi)
            if isinstance(opinion, dict):
                families = {'repaired': 'FIXED', 'partly repaired': 'PARTIAL', 'not repaired': 'NOT_FIXED'}
                agrees = None
                if opinion.get('status') == 'ok':
                    agrees = families.get(opinion.get('ai_says')) == decision.verdict
                ai_opinion = {**opinion, 'agrees': agrees}
        except Exception:
            logging.getLogger(__name__).debug('Advisory second opinion unavailable', exc_info=True)
    timings['total'] = round((perf_counter()-start)*1000, 2)
    return {
        'id': run_id, 'complaint_id': complaint_id, 'case_id': None, 'simulated': False,
        'verdict': decision.verdict, 'confidence': decision.confidence,
        'percent_resolved': pct, 'reasons': decision.reasons,
        'checks': {'location': to_dict(location), 'duplicate': to_dict(duplicate), 'scene': to_dict(scene.check), 'quality': to_dict(quality)},
        'ai_opinion': ai_opinion,
        'explanation': explanation, 'images': images, 'roi': roi, 'roi_source': roi_source,
        'location': {'lat': before_ll.lat if before_ll else None, 'lon': before_ll.lon if before_ll else None, 'ward': None},
        'timings_ms': timings, 'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
    }
