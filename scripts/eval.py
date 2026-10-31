"""Evaluate simulated repairs honestly; these are not real repair ground truth."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.make_demo_pairs import read_rois, read_image, make_after, save_image
from backend.pipeline import run
from backend.pipeline.dedupe import phash_hex
from backend.pipeline.types import LatLon

LABELS = ['FIXED','PARTIAL','NOT_FIXED','SUSPICIOUS','NEEDS_REVIEW']
KINDS = [('fixed','FIXED'),('partial','PARTIAL'),('not_fixed','NOT_FIXED'),('wrong_location','SUSPICIOUS'),('duplicate','SUSPICIOUS')]


def write_report(rows: list[dict], planned: int, path: Path, mode: str) -> None:
    """Report completed predictions separately from unavailable pipeline errors."""
    completed = [row for row in rows if 'verdict' in row]
    errors = [row for row in rows if 'error' in row]
    counts = Counter((row['expected'],row['verdict']) for row in completed)
    text = ['# Simulated-pair evaluation','',
            'All after images are simulated repairs or deliberately mismatched/reused evidence. This measures synthetic consistency, not real-world repair accuracy.', '',
            f'Mask mode: `{mode}`. Marked ROIs are supplied; optional YOLO suggestions are not required.',
            f'Planned: {planned}; completed: {len(completed)}; errors: {len(errors)}; unattempted: {planned-len(rows)}.','']
    if completed:
        correct = sum(row['verdict']==row['expected'] for row in completed)
        text += [f'Accuracy on completed pairs: {correct}/{len(completed)} ({100*correct/len(completed):.1f}%).',
                 f'Average verification time: {sum(row["elapsed_ms"] for row in completed)/len(completed):.1f} ms.','',
                 '| Expected / predicted | '+' | '.join(LABELS)+' |', '|---|'+'---:|'*len(LABELS)]
        for label in LABELS:
            text.append('| '+label+' | '+' | '.join(str(counts[label,predicted]) for predicted in LABELS)+' |')
    else:
        text += ['Accuracy and average verification time: unavailable (no completed predictions).']
    text += ['', '| Photo | Type | Seed | Expected | Actual / error | Mask | ms |','|---|---|---:|---|---|---|---:|']
    for row in rows:
        actual = row.get('verdict',row.get('error','')).replace('|','/')
        text.append(f'| {row["photo"]} | {row["kind"]} | {row["seed"]} | {row["expected"]} | {actual} | {row["mask_source"]} | {row["elapsed_ms"]:.1f} |')
    text += ['', 'Each pair is evaluated independently. Duplicate cases register the identical after image under a different complaint ID; no other test hashes contaminate repair scores.',
             'Three deterministic jitter seeds are used for every photo/type. Wrong-location pairs use another road photo and GPS approximately 140 m away.']
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(text)+'\n')
    print('\n'.join(text[:text.index('| Photo | Type | Seed | Expected | Actual / error | Mask | ms |')]))


def evaluate(raw: Path, out: Path, report: Path, mode: str = 'auto') -> int:
    """Run the pipeline over every marked photo, five pair types, three seeds."""
    rois = read_rois(raw)
    photos = list(rois)
    out.mkdir(parents=True,exist_ok=True)
    rows = []
    planned = len(photos)*len(KINDS)*3
    unavailable = False
    for photo_index,name in enumerate(photos):
        before = read_image(raw/name)
        roi = rois[name]
        wrong_path = raw/'other_1.jpg'
        if not wrong_path.exists():
            wrong_path = raw/photos[(photo_index+1)%len(photos)]
        wrong = read_image(wrong_path)
        for kind,expected in KINDS:
            for seed in range(3):
                folder = out/f'{Path(name).stem}_{kind}_{seed}'
                folder.mkdir(parents=True,exist_ok=True)
                before_path, after_path = folder/'input_before.jpg', folder/'input_after.jpg'
                source = 'none'
                if kind == 'wrong_location':
                    after = wrong
                else:
                    after,source = make_after(before,roi,'fixed' if kind=='duplicate' else kind,seed,mode)
                save_image(before_path,before)
                save_image(after_path,after)
                # Hash the decoded JPEG, exactly as the verification path does.
                known = [('earlier-complaint',phash_hex(read_image(after_path)))] if kind=='duplicate' else []
                row = {'photo':name,'kind':kind,'seed':seed,'expected':expected,'mask_source':source}
                tick = perf_counter()
                try:
                    result = run.verify(str(before_path),str(after_path),f'eval-{photo_index}-{kind}-{seed}',
                                        LatLon(12.9352,77.6245),LatLon(12.93646,77.6245) if kind=='wrong_location' else LatLon(12.93521,77.62452),
                                        roi,known,str(folder))
                    row.update(verdict=result['verdict'],percent_resolved=result['percent_resolved'])
                    (folder/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
                except NotImplementedError as error:
                    row['error'] = f'BLOCKED: pending pipeline implementation ({type(error).__name__})'
                    unavailable = True
                except (ValueError, OSError) as error:
                    row['error'] = f'{type(error).__name__}: {error}'
                row['elapsed_ms'] = (perf_counter()-tick)*1000
                rows.append(row)
                print(f'{name} {kind} seed={seed}: {expected} -> {row.get("verdict",row.get("error"))}')
                if unavailable:
                    break
            if unavailable:
                break
        if unavailable:
            break
    write_report(rows,planned,report,mode)
    (out/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    return 2 if any('error' in row for row in rows) else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw',type=Path,default=ROOT/'data/raw')
    parser.add_argument('--out',type=Path,default=ROOT/'data/runs/eval')
    parser.add_argument('--report',type=Path,default=ROOT/'docs/RESULTS.md')
    parser.add_argument('--mask-mode',choices=['auto','ellipse'],default='auto')
    args = parser.parse_args()
    raise SystemExit(evaluate(args.raw,args.out,args.report,args.mask_mode))


if __name__ == '__main__':
    main()
