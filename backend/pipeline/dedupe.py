from __future__ import annotations
import numpy as np
from .types import LatLon, CheckResult, SceneMatch, ScoreResult, Decision
from .config import MAX_SIDE

def phash_hex(bgr: np.ndarray) -> str: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def hamming(h1: str, h2: str) -> int: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
def find_duplicate(after_hash: str, known: list[tuple[str, str]], complaint_id: str) -> CheckResult: 
    """Contract stub; implementation pending."""
    raise NotImplementedError
