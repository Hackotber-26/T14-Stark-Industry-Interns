"""Coordinate verification without coupling pipeline modules to HTTP."""
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
import cv2
from . import align, dedupe, exif, match, score, segment, verdict, explain
from .types import LatLon, ScoreResult, CheckResult, to_dict


class RoiRequired(ValueError):
    """A marked box is required when the model cannot suggest one."""


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

    before = cv2.imread(before_path)
    after = cv2.imread(after_path)
    if before is None or after is None:
        raise ValueError('Upload valid before and after images')
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
    roi_source = 'marked' if roi is not None else 'model'
    quality = CheckResult('skipped', 'Not scored – photos do not match')
    if scene.check.status == 'pass':
        aligned = timed('align', align.warp_after_to_before, after, scene.H, before.shape)
        valid = align.valid_region_mask(after.shape, scene.H, before.shape)
        if roi is None:
            roi, _ = timed('detect', segment.get_detector().suggest_roi, before)
        if roi is None:
            raise RoiRequired('Mark the pothole on the before photo')
        pct, before_area, remaining_area, before_mask, after_mask = timed('score', score.percent_resolved, before, aligned, roi, valid)
        quality = score.patch_quality(aligned, before_mask)
        measurement = ScoreResult(pct, before_area, remaining_area, quality)
        images['after_aligned'] = write('after_aligned', aligned)
        images['heatmap'] = write('heatmap', score.heatmap(before, before_mask, after_mask))
    decision = timed('verdict', verdict.decide, location, duplicate, scene.check, measurement)
    explanation = timed('explain', explain.explain, decision, pct)
    timings['total'] = round((perf_counter()-start)*1000, 2)
    return {
        'id': run_id, 'complaint_id': complaint_id, 'case_id': None, 'simulated': False,
        'verdict': decision.verdict, 'confidence': decision.confidence,
        'percent_resolved': pct, 'reasons': decision.reasons,
        'checks': {'location': to_dict(location), 'duplicate': to_dict(duplicate), 'scene': to_dict(scene.check), 'quality': to_dict(quality)},
        'explanation': explanation, 'images': images, 'roi': roi, 'roi_source': roi_source,
        'location': {'lat': before_ll.lat if before_ll else None, 'lon': before_ll.lon if before_ll else None, 'ward': None},
        'timings_ms': timings, 'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
    }
