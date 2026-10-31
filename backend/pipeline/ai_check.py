"""Optional offline CLIP second opinion for aligned marked-box crops."""
from __future__ import annotations

from threading import Lock

import cv2
import numpy as np

_MODEL_ID = 'openai/clip-vit-base-patch32'
_PROMPTS = ['a photo of a pothole in a road',
            'a photo of a road with a hole full of water',
            'a photo of smooth undamaged asphalt road',
            'a photo of a freshly repaired road patch']
_model = None
_processor = None
_device = None
_attempted = False
_lock = Lock()


def _load_model() -> tuple:
    """Load only cached assets and choose the local inference device."""
    import torch
    from transformers import CLIPModel, CLIPProcessor

    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    processor = CLIPProcessor.from_pretrained(_MODEL_ID, local_files_only=True)
    model = CLIPModel.from_pretrained(_MODEL_ID, local_files_only=True).to(device).eval()
    return model, processor, device


def warm_up():
    """Attempt model initialization once; optional inference must never raise."""
    global _model, _processor, _device, _attempted
    try:
        with _lock:
            if _attempted:
                return
            _attempted = True
            _model, _processor, _device = _load_model()
    except Exception:
        _model = _processor = _device = None


def _damage_probability(bgr: np.ndarray) -> float:
    """Score the damage prompts relative to all four descriptions."""
    import torch
    from PIL import Image

    image = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    inputs = _processor(text=_PROMPTS, images=image, return_tensors='pt', padding=True)
    inputs = {key: value.to(_device) for key, value in inputs.items()}
    with torch.inference_mode():
        probabilities = _model(**inputs).logits_per_image.softmax(dim=-1)
    value = float(probabilities[0, :2].sum().cpu())
    if not np.isfinite(value):
        raise ValueError('Non-finite model score')
    return value


def _crop(bgr: np.ndarray, roi) -> np.ndarray:
    """Crop the normalized polygon bounds with 15% padding on each side."""
    h, w = bgr.shape[:2]
    points = np.asarray(roi, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or not np.all(np.isfinite(points)):
        raise ValueError('Invalid marked box')
    low, high = points.min(axis=0), points.max(axis=0)
    if np.any(low >= high):
        raise ValueError('Empty marked box')
    pad = (high - low) * 0.15
    x0, y0 = np.floor(np.clip(low - pad, 0, 1) * [w, h]).astype(int)
    x1, y1 = np.ceil(np.clip(high + pad, 0, 1) * [w, h]).astype(int)
    if x1 <= x0 or y1 <= y0:
        raise ValueError('Empty crop')
    return bgr[y0:y1, x0:x1]


def ai_second_opinion(before_bgr, after_aligned_bgr, roi) -> dict | None:
    """Return an optional second opinion without changing pipeline verdicts."""
    try:
        warm_up()
        if _model is None or _processor is None:
            return None
        before = _damage_probability(_crop(before_bgr, roi))
        if before < 0.5:
            return {'status': 'no_damage_recognised', 'damage_before': round(before, 2),
                    'damage_after': None, 'ai_says': None}
        after = _damage_probability(_crop(after_aligned_bgr, roi))
        if after < 0.5 and before - after >= 0.3:
            says = 'repaired'
        elif after >= 0.6:
            says = 'not repaired'
        else:
            says = 'partly repaired'
        return {'status': 'ok', 'damage_before': round(before, 2),
                'damage_after': round(after, 2), 'ai_says': says}
    except Exception:
        return None
