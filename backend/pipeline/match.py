from __future__ import annotations
import numpy as np
from .types import LatLon, CheckResult, SceneMatch, ScoreResult, Decision
from .config import MAX_SIDE

def haversine_m(a: LatLon, b: LatLon) -> float: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def gps_check(before: LatLon | None, after: LatLon | None) -> CheckResult: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def scene_match(before_bgr: np.ndarray, after_bgr: np.ndarray) -> SceneMatch: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
