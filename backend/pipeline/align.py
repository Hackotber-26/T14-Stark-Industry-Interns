"""Resize and align BGR images."""
import cv2
import numpy as np
from .config import MAX_SIDE


def resize_max_side(img: np.ndarray, max_side: int = MAX_SIDE) -> np.ndarray:
    """Shrink images while preserving aspect ratio."""
    h, w = img.shape[:2]
    if max(h, w) <= max_side:
        return img
    scale = max_side / max(h, w)
    return cv2.resize(img, (max(1, round(w*scale)), max(1, round(h*scale))), interpolation=cv2.INTER_AREA)


def warp_after_to_before(after_bgr: np.ndarray, H: np.ndarray, before_shape: tuple) -> np.ndarray:
    """Warp the after image into before coordinates."""
    return cv2.warpPerspective(after_bgr, H, (before_shape[1], before_shape[0]))


def valid_region_mask(after_shape: tuple, H: np.ndarray, before_shape: tuple) -> np.ndarray:
    """Mark pixels covered by real after-image data."""
    return cv2.warpPerspective(np.full(after_shape[:2], 255, np.uint8), H, (before_shape[1], before_shape[0]), flags=cv2.INTER_NEAREST)
