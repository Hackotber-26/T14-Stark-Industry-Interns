from __future__ import annotations

from .config import FIXED_MIN_PCT, PARTIAL_MIN_PCT
from .types import CheckResult, ScoreResult, Decision


def decide(location: CheckResult, duplicate: CheckResult, scene: CheckResult,
           score: ScoreResult | None) -> Decision:
    """Apply fraud checks before repair thresholds and quality checks."""
    pct = score.percent_resolved if score is not None else None
    quality = score.quality.status if score is not None else 'skipped'
    confidence = 0.92
    confidence -= {'skipped': 0.15, 'warn': 0.10}.get(location.status, 0)
    if pct is not None and min(abs(pct - FIXED_MIN_PCT), abs(pct - PARTIAL_MIN_PCT)) <= 7:
        confidence -= 0.15
    if quality == 'warn':
        confidence -= 0.10
    if scene.status == 'pass':
        confidence *= 0.85 + 0.15 * min((scene.inlier_ratio or 0) / 0.5, 1)
    confidence = round(max(0.30, min(0.99, confidence)), 2)
    reasons = []
    for name, check in (('location', location), ('duplicate', duplicate), ('scene', scene)):
        if check.status == 'fail':
            reasons.append(f'{name.capitalize()} check failed: {check.detail}' if check.detail
                           else {'location': 'The photos were taken at different locations',
                                 'duplicate': 'Duplicate photo used for another complaint',
                                 'scene': 'The photos do not show the same scene'}[name])
    if reasons:
        return Decision('SUSPICIOUS', confidence, reasons)
    if pct is None:
        return Decision('NEEDS_REVIEW', confidence, ['No clear damage found inside the marked box'])
    if pct >= FIXED_MIN_PCT:
        if quality == 'fail':
            return Decision('PARTIAL', confidence, ['Patch quality looks poor',
                            f'{pct:g}% of the original pothole area is repaired'])
        return Decision('FIXED', confidence, [f'{pct:g}% of the original pothole area is repaired'])
    if pct >= PARTIAL_MIN_PCT:
        return Decision('PARTIAL', confidence, [f'Only {pct:g}% of the original pothole area is repaired'])
    return Decision('NOT_FIXED', confidence, [f'Only {pct:g}% of the original pothole area is repaired; the pothole remains'])
