from __future__ import annotations

import os
from pathlib import Path
import numpy as np

from .config import ROI_PAD, SEG_IMGSZ, SEG_SUGGEST_CONF


class DefectDetector:
    def __init__(self, weights_path: str | None = None, device: str | None = None):
        """Defer optional model loading until a suggestion is requested."""
        self.weights_path = weights_path or os.environ.get('FIXCHECK_WEIGHTS')
        self.device = device
        self._model = None
        self._attempted = False

    def suggest_roi(self, bgr: np.ndarray) -> tuple[list[list[float]] | None, float]:
        """Suggest the most confident pothole box; failures yield no suggestion."""
        if os.environ.get('FIXCHECK_MOCK_SEG') == '1':
            return None, 0.0
        try:
            if not self._attempted:
                self._attempted = True
                if not self.weights_path or not Path(self.weights_path).is_file():
                    return None, 0.0
                import torch
                from ultralytics import YOLO
                self.device = self.device or ('mps' if torch.backends.mps.is_available() else 'cpu')
                self._model = YOLO(self.weights_path)
            if self._model is None:
                return None, 0.0
            results = self._model.predict(bgr, conf=SEG_SUGGEST_CONF, imgsz=SEG_IMGSZ,
                                          verbose=False, device=self.device)
            best = None
            for result in results:
                if result.boxes is None:
                    continue
                for box in result.boxes:
                    name = str(result.names[int(box.cls.item())]).lower()
                    confidence = float(box.conf.item())
                    if 'pothole' in name and confidence >= SEG_SUGGEST_CONF:
                        if best is None or confidence > best[0]:
                            best = (confidence, box.xyxy[0].cpu().numpy())
            if best is None:
                return None, 0.0
            confidence, (x0, y0, x1, y1) = best
            dx, dy = (x1 - x0) * ROI_PAD, (y1 - y0) * ROI_PAD
            h, w = bgr.shape[:2]
            x0, x1 = np.clip([(x0 - dx) / w, (x1 + dx) / w], 0, 1).tolist()
            y0, y1 = np.clip([(y0 - dy) / h, (y1 + dy) / h], 0, 1).tolist()
            return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], confidence
        except Exception:
            return None, 0.0


_detector: DefectDetector | None = None


def get_detector() -> DefectDetector:
    """Return the process-wide optional detector."""
    global _detector
    if _detector is None:
        _detector = DefectDetector()
    return _detector
