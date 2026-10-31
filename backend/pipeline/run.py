from __future__ import annotations
import numpy as np
from .types import LatLon, CheckResult, SceneMatch, ScoreResult, Decision
from .config import MAX_SIDE

def verify(before_path: str, after_path: str, complaint_id: str,
           before_ll: LatLon | None, after_ll: LatLon | None,
           roi: list | None, known_hashes: list[tuple[str, str]],
           out_dir: str) -> dict: 
        """Contract stub; implementation pending."""
        raise NotImplementedError
