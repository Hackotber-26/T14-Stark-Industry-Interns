"""FixCheck upload, demo, and result API."""
from contextlib import asynccontextmanager
import json
import logging
import math
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Thread
import shutil
from uuid import uuid4
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from . import store, report
from ..pipeline import run, segment, dedupe, exif
from ..pipeline.types import LatLon

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / 'data/demo'
RUNS_DIR = ROOT / 'data/runs'
for folder in (DEMO_DIR, RUNS_DIR):
    folder.mkdir(parents=True, exist_ok=True)


def _cases():
    """Read available case metadata; no demo data is also valid."""
    cases = []
    paths = [path for path in DEMO_DIR.glob('case_*/meta.json') if path.parent.name[5:].isdigit()]
    for path in sorted(paths, key=lambda path: int(path.parent.name[5:])):
        meta = json.loads(path.read_text())
        if meta.get('case_id') != path.parent.name:
            continue
        cases.append((path.parent, meta))
    return cases


def _warm_up_ai() -> None:
    """Warm the optional model off the startup path; failures are advisory only."""
    try:
        from ..pipeline.ai_check import warm_up
        warm_up()
    except Exception:
        logging.getLogger(__name__).debug('Advisory model warm-up unavailable', exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cases = _cases()
    for _, meta in cases:
        store.delete_hashes(meta['complaint_id'])
    for folder, meta in cases:
        try:
            image = exif.read_bgr(str(folder / 'after.jpg'))
        except exif.UnreadableImage:
            continue
        store.add_hash(meta['complaint_id'], dedupe.phash_hex(image))
    if run.ai_enabled():
        Thread(target=_warm_up_ai, name='advisory-warm-up', daemon=True).start()
    yield


app = FastAPI(title='FixCheck', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173'], allow_methods=['*'], allow_headers=['*'])
app.mount('/files', StaticFiles(directory=RUNS_DIR), name='files')
app.mount('/demo-files', StaticFiles(directory=DEMO_DIR), name='demo-files')


@app.get('/api/health')
def health():
    detector = getattr(segment, '_detector', None)
    loaded = detector is not None and (getattr(detector, 'model', None) is not None or getattr(detector, '_model', None) is not None)
    return {'ok': True, 'model_loaded': loaded, 'mock_seg': os.getenv('FIXCHECK_MOCK_SEG') == '1'}


@app.get('/api/demo')
def demos():
    return [{**{key: meta[key] for key in ('case_id','title','expected','simulated','ward')}, 'before_url': f'/demo-files/{folder.name}/before.jpg', 'after_url': f'/demo-files/{folder.name}/after.jpg'} for folder, meta in _cases()]


def _roi(value):
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError('ROI must contain four normalized corners')
    for point in value:
        if not isinstance(point, list) or len(point) != 2 or any(isinstance(x, bool) or not isinstance(x, (int,float)) or not math.isfinite(x) or not 0 <= x <= 1 for x in point):
            raise ValueError('ROI coordinates must be between 0 and 1')
    if cv2.contourArea(np.array(value, dtype=np.float32)) <= 0:
        raise ValueError('ROI must have a positive area')
    return value


def _gps(lat, lon):
    if lat is None and lon is None:
        return None
    if lat is None or lon is None or not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError('GPS requires valid latitude and longitude')
    return LatLon(lat, lon)


def _known_hashes(meta=None):
    """Demo evidence sees earlier numbered cases and existing real uploads."""
    hashes = store.all_hashes()
    if meta is None:
        return hashes
    case_numbers = {case['complaint_id']: int(case['case_id'][5:]) for _, case in _cases()}
    current = int(meta['case_id'][5:])
    return [(complaint_id, value) for complaint_id, value in hashes
            if complaint_id not in case_numbers or case_numbers[complaint_id] < current]


def _perform(before, after, complaint_id, before_ll, after_ll, roi, folder, meta=None):
    try:
        result = run.verify(str(before), str(after), complaint_id, before_ll, after_ll, roi, _known_hashes(meta), str(folder))
        if meta:
            result.update(case_id=meta['case_id'], simulated=meta.get('simulated', False))
            result['location']['ward'] = meta.get('ward')
        store.save_result(result)
        image = exif.read_bgr(str(after))
        store.add_hash(complaint_id, dedupe.phash_hex(image))
        return result
    except exif.UnreadableImage as error:
        shutil.rmtree(folder, ignore_errors=True)
        raise HTTPException(400, str(error)) from error
    except ValueError as error:
        shutil.rmtree(folder, ignore_errors=True)
        raise HTTPException(422, str(error)) from error
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise


@app.post('/api/demo/{case_id}/verify')
def demo_verify(case_id: str):
    for folder, meta in _cases():
        if meta['case_id'] == case_id:
            before_gps, after_gps = meta.get('before_gps'), meta.get('after_gps')
            return _perform(folder/'before.jpg', folder/'after.jpg', meta['complaint_id'], _gps(**before_gps) if before_gps else None, _gps(**after_gps) if after_gps else None, _roi(meta.get('roi')), RUNS_DIR/f'r_{uuid4().hex[:12]}', meta)
    raise HTTPException(404, 'Demo case not found')


@app.post('/api/verify')
def verify(before: UploadFile = File(...), after: UploadFile = File(...), complaint_id: str = Form(...), roi: str | None = Form(None), before_lat: float | None = Form(None), before_lon: float | None = Form(None), after_lat: float | None = Form(None), after_lon: float | None = Form(None)):
    try:
        box = _roi(json.loads(roi) if roi is not None else None)
        before_ll, after_ll = _gps(before_lat, before_lon), _gps(after_lat, after_lon)
        if not complaint_id.strip():
            raise ValueError('Complaint ID is required')
    except (ValueError, TypeError) as error:
        raise HTTPException(422, str(error)) from error
    folder = RUNS_DIR/f'r_{uuid4().hex[:12]}'
    folder.mkdir(parents=True)
    try:
        # Preserve original bytes for EXIF; processed images are written separately.
        before_path, after_path = folder/'before_upload', folder/'after_upload'
        with before_path.open('wb') as target:
            shutil.copyfileobj(before.file, target)
        with after_path.open('wb') as target:
            shutil.copyfileobj(after.file, target)
        return _perform(before_path, after_path, complaint_id, before_ll, after_ll, box, folder)
    finally:
        for name in ('before_upload', 'after_upload'):
            (folder/name).unlink(missing_ok=True)


@app.post('/api/suggest-roi')
def suggest(before: UploadFile = File(...)):
    try:
        image = exif.read_bgr(before.file)
    except exif.UnreadableImage as error:
        raise HTTPException(400, str(error)) from error
    roi, confidence = segment.get_detector().suggest_roi(image)
    return {'roi': roi, 'confidence': float(confidence)}


@app.get('/api/results')
def results():
    return store.list_results()


@app.get('/api/results/{id}')
def result(id: str):
    value = store.get_result(id)
    if value is None:
        raise HTTPException(404, 'Result not found')
    return value


@app.get('/api/results/{id}/report.pdf')
def result_report(id: str):
    """Download an evidence report for an existing result."""
    value = store.get_result(id)
    if value is None:
        raise HTTPException(404, 'Result not found')
    # Each download has its own output file so concurrent requests cannot clash.
    with NamedTemporaryFile(suffix='.pdf', prefix='report_', dir=RUNS_DIR, delete=False) as output:
        path = Path(output.name)
    try:
        report.build_report(value, str(path))
        return FileResponse(path, media_type='application/pdf', filename=f'{value["id"]}-report.pdf',
                            background=BackgroundTask(path.unlink, missing_ok=True))
    except Exception:
        path.unlink(missing_ok=True)
        raise
