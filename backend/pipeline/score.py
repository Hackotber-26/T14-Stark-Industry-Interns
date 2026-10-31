from __future__ import annotations
import numpy as np
from .types import LatLon, CheckResult, SceneMatch, ScoreResult, Decision
from .config import MAX_SIDE

def roi_to_mask(shape: tuple, roi_norm: list[list[float]]) -> np.ndarray: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def defect_mask(bgr: np.ndarray, roi_norm, valid: np.ndarray | None = None) -> np.ndarray: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def percent_resolved(before_bgr, after_aligned_bgr, roi_norm, valid_mask) -> tuple: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def patch_quality(after_aligned_bgr, before_mask) -> CheckResult: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def heatmap(before_bgr, before_mask, after_mask_aligned) -> np.ndarray: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
