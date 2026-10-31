"""Perceptual hashes detect reused evidence."""
import cv2
import imagehash
import numpy as np
from PIL import Image
from .config import PHASH_DUP_MAX_HAMMING
from .types import CheckResult


def phash_hex(bgr: np.ndarray) -> str:
    """Compute a perceptual hash from a BGR image."""
    return str(imagehash.phash(Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))))


def hamming(h1: str, h2: str) -> int:
    """Count differing hash bits."""
    return int((int(h1, 16) ^ int(h2, 16)).bit_count())


def find_duplicate(after_hash: str, known: list[tuple[str, str]], complaint_id: str) -> CheckResult:
    """Find the closest hash belonging to another complaint."""
    candidates = [(hamming(after_hash, value), cid) for cid, value in known if cid != complaint_id]
    if not candidates:
        return CheckResult('pass', 'No earlier use of this photo found')
    distance, cid = min(candidates)
    duplicate = distance <= PHASH_DUP_MAX_HAMMING
    return CheckResult('fail' if duplicate else 'pass', 'Photo used for another complaint' if duplicate else 'No earlier use of this photo found', hamming=distance, matched_complaint_id=cid if duplicate else None)
