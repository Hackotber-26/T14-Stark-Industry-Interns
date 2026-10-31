from __future__ import annotations
import numpy as np
from .types import LatLon, CheckResult, SceneMatch, ScoreResult, Decision
from .config import MAX_SIDE

def decide(location: CheckResult, duplicate: CheckResult, scene: CheckResult,
           score: ScoreResult | None) -> Decision: 
        """Contract stub; implementation pending."""
        raise NotImplementedError
