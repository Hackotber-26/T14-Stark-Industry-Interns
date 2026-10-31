from __future__ import annotations
import numpy as np
from .types import LatLon, CheckResult, SceneMatch, ScoreResult, Decision
from .config import MAX_SIDE

def resize_max_side(img: np.ndarray, max_side: int = MAX_SIDE) -> np.ndarray: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def warp_after_to_before(after_bgr: np.ndarray, H: np.ndarray, before_shape: tuple) -> np.ndarray: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def valid_region_mask(after_shape: tuple, H: np.ndarray, before_shape: tuple) -> np.ndarray: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
