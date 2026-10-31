from __future__ import annotations
import numpy as np
from .types import LatLon, CheckResult, SceneMatch, ScoreResult, Decision
from .config import MAX_SIDE

class DefectDetector:
    def __init__(self, weights_path: str | None = None, device: str | None = None): 
        """Contract stub; implementation pending."""
        raise NotImplementedError
    def suggest_roi(self, bgr: np.ndarray) -> tuple[list[list[float]] | None, float]: 
        """Contract stub; implementation pending."""
        raise NotImplementedError
def get_detector() -> DefectDetector: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
