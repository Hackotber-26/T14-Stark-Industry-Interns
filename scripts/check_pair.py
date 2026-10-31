"""Check venue photos from the repository root (with the Python venv active).

Usage: python scripts/check_pair.py BEFORE AFTER --roi x0,y0,x1,y1 [--out DIR]
Box coordinates are normalized to 0..1 on BEFORE. Output defaults to
 data/runs/check. Each run replaces images of the same name in that directory.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.pipeline.run import verify


def parse_roi(value: str) -> list[list[float]]:
    """Validate normalized corners and expand them to the pipeline polygon."""
    try:
        x0, y0, x1, y1 = [float(part) for part in value.split(',')]
    except ValueError as exc:
        raise argparse.ArgumentTypeError('ROI must be x0,y0,x1,y1') from exc
    if not all(math.isfinite(v) and 0 <= v <= 1 for v in (x0, y0, x1, y1)):
        raise argparse.ArgumentTypeError('ROI coordinates must be finite and between 0 and 1')
    if x0 >= x1 or y0 >= y1:
        raise argparse.ArgumentTypeError('ROI requires x0 < x1 and y0 < y1')
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def main() -> None:
    """Run the full pipeline using photo GPS when available."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--roi', required=True, type=parse_roi)
    parser.add_argument('--out', type=Path, default=Path('data/runs/check'))
    args = parser.parse_args()
    for path in (args.before, args.after):
        if not path.is_file():
            parser.error(f'Photo does not exist: {path}')
    try:
        result = verify(str(args.before), str(args.after), 'VENUE-CHECK',
                        None, None, args.roi, [], str(args.out))
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Verification failed: {exc}\n')
    pct = result['percent_resolved']
    print(f"Verdict: {result['verdict']}")
    print(f"Repaired: {pct:g}%" if pct is not None else 'Repaired: unavailable')
    timings = result.get('timings_ms', {})
    for name, check in result['checks'].items():
        duration = timings.get(name)
        timing = f'{duration:.2f} ms' if duration is not None else 'not separately timed'
        print(f"{name}: {check['status']} ({timing}) — {check.get('detail', '')}")
    print('Pipeline timings:')
    for name, duration in timings.items():
        print(f'  {name}: {duration:.2f} ms')
    print('Duplicate check uses an empty history for this standalone run.')
    for key in ('after_aligned', 'heatmap'):
        if result['images'].get(key):
            print(f'{key}: {(args.out / (key + ".jpg")).resolve()}')
        else:
            print(f'{key}: unavailable (scene check did not pass)')


if __name__ == '__main__':
    main()
