"""Build reproducible, explicitly simulated repair pairs (SPEC section 8)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys
import warnings
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.pipeline import score
from backend.pipeline.align import resize_max_side
from backend.pipeline.config import RING_PX, TEXTURE_WIN

SEED = 0
# These are synthesis settings from SPEC section 8, not scoring thresholds.
REPAIR_DILATE = 9
INPAINT_RADIUS = 9
JITTER_FRACTION = 0.025
BRIGHTNESS_FRACTION = 0.08
CASES = [
    ('case_01', 'pothole_9.jpg', 'fixed', 'FIXED', 'Pothole marked resolved – honest repair'),
    ('case_02', 'pothole_4.jpg', 'partial', 'PARTIAL', 'Only half the pothole repaired'),
    ('case_03', 'pothole_5.jpg', 'not_fixed', 'NOT_FIXED', 'Pothole still unrepaired'),
    ('case_04', 'pothole_7.jpg', 'wrong_location', 'SUSPICIOUS', 'Photo from a different road'),
    ('case_05', 'pothole_2.jpg', 'duplicate', 'SUSPICIOUS', 'Repair photo reused for another complaint'),
]


def read_image(path: Path) -> np.ndarray:
    """Load and resize a source image, failing clearly if it is missing."""
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f'Cannot read source photo: {path}')
    return resize_max_side(image)


def read_rois(raw: Path) -> dict[str, list]:
    """Load marked boxes while ignoring metadata entries."""
    return {name: roi for name, roi in json.loads((raw/'rois.json').read_text()).items() if not name.startswith('_')}


def box_mask(shape: tuple, roi: list) -> np.ndarray:
    """Rasterize normalized box corners independently of pending score code."""
    h, w = shape[:2]
    points = np.rint(np.array(roi)*[w,h]).astype(np.int32)
    mask = np.zeros((h,w),np.uint8)
    cv2.fillPoly(mask,[points],255)
    return mask


def repair_mask(before: np.ndarray, roi: list, mode: str = 'auto') -> tuple[np.ndarray, str]:
    """Use measured damage when available, otherwise an inscribed ellipse."""
    mask = None
    reason = 'ellipse explicitly requested'
    if mode == 'auto':
        try:
            mask = score.defect_mask(before, roi)
            if not np.any(mask):
                reason = 'defect_mask returned an empty mask'
                mask = None
        except NotImplementedError:
            reason = 'defect_mask is not implemented yet'
    if mask is not None:
        return cv2.dilate(mask,np.ones((REPAIR_DILATE,REPAIR_DILATE),np.uint8)), 'defect_mask'
    warnings.warn(f'{reason}; using ellipse fallback', stacklevel=2)
    h, w = before.shape[:2]
    points = np.array(roi)*[w,h]
    low, high = points.min(axis=0), points.max(axis=0)
    center = tuple(np.rint((low+high)/2).astype(int))
    axes = tuple(np.maximum(1,np.floor((high-low)/2)).astype(int))
    mask = np.zeros((h,w),np.uint8)
    cv2.ellipse(mask,center,axes,0,0,360,255,-1)
    return mask, 'ellipse_fallback'


def fill_repair(before: np.ndarray, mask: np.ndarray, roi: list, rng: np.random.Generator) -> np.ndarray:
    """Inpaint damage and restore surrounding-road noise inside the mask."""
    if not np.any(mask):
        return before.copy()
    repaired = cv2.inpaint(before,mask,INPAINT_RADIUS,cv2.INPAINT_TELEA)
    box = box_mask(before.shape,roi)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*RING_PX+1,2*RING_PX+1))
    ring = (cv2.dilate(box,kernel)>0) & (box==0)
    gray = cv2.cvtColor(before,cv2.COLOR_BGR2GRAY).astype(np.float32)
    mean = cv2.blur(gray,(TEXTURE_WIN,TEXTURE_WIN))
    local_std = np.sqrt(np.maximum(cv2.blur(gray*gray,(TEXTURE_WIN,TEXTURE_WIN))-mean*mean,0))
    sigma = float(np.median(local_std[ring])) if np.any(ring) else 0.0
    noisy = np.clip(repaired.astype(np.float32)+rng.normal(0,sigma,repaired.shape),0,255).astype(np.uint8)
    repaired[mask>0] = noisy[mask>0]
    blurred = cv2.GaussianBlur(repaired,(3,3),0)
    repaired[mask>0] = blurred[mask>0]
    return repaired


def jitter(image: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Simulate small camera motion and brightness changes with a fixed RNG."""
    h, w = image.shape[:2]
    corners = np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
    offsets = rng.uniform(-JITTER_FRACTION,JITTER_FRACTION,(4,2))*[w,h]
    H = cv2.getPerspectiveTransform(corners,(corners+offsets).astype(np.float32))
    warped = cv2.warpPerspective(image,H,(w,h),borderMode=cv2.BORDER_REFLECT_101)
    return np.clip(warped.astype(np.float32)*rng.uniform(1-BRIGHTNESS_FRACTION,1+BRIGHTNESS_FRACTION),0,255).astype(np.uint8)


def make_after(before: np.ndarray, roi: list, kind: str, seed: int, mode: str = 'auto') -> tuple[np.ndarray, str]:
    """Synthesize a fixed, half-fixed, or unchanged image, then jitter it."""
    rng = np.random.default_rng(seed)
    if kind == 'not_fixed':
        return jitter(before,rng), 'none'
    mask, source = repair_mask(before,roi,mode)
    if kind == 'partial':
        x, _, width, _ = cv2.boundingRect(mask)
        x_mid = x + width // 2
        mask[:,x_mid:] = 0
    elif kind != 'fixed':
        raise ValueError(f'Unknown repair kind: {kind}')
    return jitter(fill_repair(before,mask,roi,rng),rng), source


def save_image(path: Path, image: np.ndarray) -> None:
    """Write an image and fail if the output cannot be written."""
    if not cv2.imwrite(str(path),image):
        raise OSError(f'Cannot write image: {path}')


def preview(out: Path, metas: list[dict]) -> None:
    """Create a labelled five-row contact sheet with marked before boxes."""
    cell_w, cell_h, label_h = 480, 320, 54
    sheet = np.full((len(metas)*(cell_h+label_h),2*cell_w,3),24,np.uint8)
    for row, meta in enumerate(metas):
        y = row*(cell_h+label_h)
        for column, name in enumerate(('before','after')):
            image = cv2.imread(str(out/meta['case_id']/f'{name}.jpg'))
            if name == 'before':
                h,w = image.shape[:2]
                points = np.rint(np.array(meta['roi'])*[w,h]).astype(np.int32)
                cv2.polylines(image,[points],True,(0,230,255),2)
            scale = min(cell_w/image.shape[1],cell_h/image.shape[0])
            thumb = cv2.resize(image,(round(image.shape[1]*scale),round(image.shape[0]*scale)))
            x0 = column*cell_w+(cell_w-thumb.shape[1])//2
            y0 = y+label_h+(cell_h-thumb.shape[0])//2
            sheet[y0:y0+thumb.shape[0],x0:x0+thumb.shape[1]] = thumb
            text = f"{meta['case_id']} {name.upper()} | {meta['expected']}"
            cv2.putText(sheet,text,(column*cell_w+10,y+22),cv2.FONT_HERSHEY_SIMPLEX,.48,(240,240,240),1,cv2.LINE_AA)
            cv2.putText(sheet,'SIMULATED REPAIR (DEMO)',(column*cell_w+10,y+43),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,210,255),1,cv2.LINE_AA)
    save_image(out/'_preview.jpg',sheet)


def generate(raw: Path, out: Path, mode: str = 'auto') -> list[dict]:
    """Write all five specified cases and a contact sheet."""
    rois = read_rois(raw)
    out.mkdir(parents=True,exist_ok=True)
    metas = []
    for index,(case_id,name,kind,expected,title) in enumerate(CASES,1):
        folder = out/case_id
        folder.mkdir(parents=True,exist_ok=True)
        before = read_image(raw/name)
        roi = rois[name]
        source = 'none'
        if kind in ('fixed','partial','not_fixed'):
            after, source = make_after(before,roi,kind,SEED+index,mode)
        elif kind == 'wrong_location':
            after = read_image(raw/'other_1.jpg')
        else:
            after = None
        save_image(folder/'before.jpg',before)
        if after is None:
            # Copy bytes, rather than re-encoding, for exact reused evidence.
            shutil.copyfile(out/'case_01/after.jpg',folder/'after.jpg')
        else:
            save_image(folder/'after.jpg',after)
        meta = {'case_id':case_id,'title':title,'complaint_id':f'BLR-DEMO-{index:04d}',
                'issue_type':'pothole','ward':'Ward A','expected':expected,'simulated':True,
                'before_gps':{'lat':12.9352,'lon':77.6245},
                'after_gps':{'lat':12.93646,'lon':77.6245} if kind=='wrong_location' else {'lat':12.93521,'lon':77.62452},
                'roi':roi,'repair_mask_source':source,'seed':SEED+index,
                'source_photo':name}
        (folder/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        metas.append(meta)
        print(f'{case_id}: {name}, {kind}, mask={source}, expected={expected}')
    preview(out,metas)
    return metas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw',type=Path,default=ROOT/'data/raw')
    parser.add_argument('--out',type=Path,default=ROOT/'data/demo')
    parser.add_argument('--mask-mode',choices=['auto','ellipse'],default='auto',help='auto uses defect_mask whenever it is implemented and nonempty')
    args = parser.parse_args()
    generate(args.raw,args.out,args.mask_mode)


if __name__ == '__main__':
    main()
