"""Save marked-box defect previews for the local source photographs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.pipeline.config import MAX_SIDE
from backend.pipeline.score import defect_mask, roi_to_mask


def main() -> None:
    """Measure every marked source image without loading a model."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, default=Path('data/raw'))
    args = parser.parse_args()
    output = args.raw / '_check'
    output.mkdir(parents=True, exist_ok=True)
    rois = json.loads((args.raw / 'rois.json').read_text())
    for name, roi in rois.items():
        if name.startswith('_'):
            continue
        image = cv2.imread(str(args.raw / name))
        if image is None:
            raise ValueError(f'Cannot read {args.raw / name}')
        h, w = image.shape[:2]
        if max(h, w) > MAX_SIDE:
            scale = MAX_SIDE / max(h, w)
            image = cv2.resize(image, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
        mask = defect_mask(image, roi)
        box = roi_to_mask(image.shape, roi)
        preview = image.copy()
        preview[mask > 0] = (0.55 * image[mask > 0] + 0.45 * np.array([68, 68, 239])).astype(np.uint8)
        contours, _ = cv2.findContours(box, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(preview, contours, -1, (255, 255, 255), 2)
        target = output / f'{Path(name).stem}_defect.jpg'
        if not cv2.imwrite(str(target), preview):
            raise OSError(f'Cannot write {target}')
        fraction = 100 * np.count_nonzero(mask) / max(np.count_nonzero(box), 1)
        print(f'{name}: {fraction:.1f}% of box → {target}')


if __name__ == '__main__':
    main()
