from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
import numpy as np

Status = Literal["pass", "warn", "fail", "skipped"]
Verdict = Literal["FIXED", "PARTIAL", "NOT_FIXED", "SUSPICIOUS", "NEEDS_REVIEW"]

@dataclass
class LatLon:
    lat: float
    lon: float

@dataclass
class CheckResult:
    status: Status
    detail: str = ""
    distance_m: Optional[float] = None      # location check
    inliers: Optional[int] = None           # scene check
    inlier_ratio: Optional[float] = None    # scene check
    matched_complaint_id: Optional[str] = None  # duplicate check
    hamming: Optional[int] = None           # duplicate check
    score: Optional[float] = None           # quality check (0..1)

@dataclass
class SceneMatch:
    check: CheckResult
    H: Optional[np.ndarray] = None          # 3x3 homography mapping AFTER pixel coords -> BEFORE pixel coords

@dataclass
class ScoreResult:
    percent_resolved: Optional[float]       # 0..100, None if not computable
    before_area_px: int
    remaining_area_px: int
    quality: CheckResult

@dataclass
class Decision:
    verdict: Verdict
    confidence: float                       # 0..1
    reasons: list[str] = field(default_factory=list)

def to_dict(obj) -> dict:
    d = asdict(obj)
    d.pop("H", None)
    return d
