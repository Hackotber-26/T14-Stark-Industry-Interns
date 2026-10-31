"""FixCheck HTTP contract scaffold."""
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
app = FastAPI(title="FixCheck")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
for folder, route in [("data/runs", "/files"), ("data/demo", "/demo-files")]:
    Path(folder).mkdir(parents=True, exist_ok=True)
    app.mount(route, StaticFiles(directory=folder), name=route[1:])
SAMPLE = {'id': 'r_8f3a2c', 'complaint_id': 'BLR-DEMO-0002', 'case_id': 'case_02', 'simulated': True, 'verdict': 'PARTIAL', 'confidence': 0.81, 'percent_resolved': 54.3, 'reasons': ['Only 54% of the original pothole area is repaired', 'Same location confirmed (4 m apart, 286 matching points)'], 'checks': {'location': {'status': 'pass', 'detail': 'Photos taken 4 m apart', 'distance_m': 4.1}, 'duplicate': {'status': 'pass', 'detail': 'No earlier use of this photo found', 'hamming': 31}, 'scene': {'status': 'pass', 'detail': '286 matching points (44%) – same scene', 'inliers': 286, 'inlier_ratio': 0.44}, 'quality': {'status': 'warn', 'detail': 'Patch surface looks uneven', 'score': 0.52}}, 'explanation': {'en': 'Partial repair. Only 54% of the original pothole has been fixed. Re-inspection needed.', 'kn': 'ಭಾಗಶಃ ದುರಸ್ತಿ. ಮೂಲ ಗುಂಡಿಯ 54% ಭಾಗ ಮಾತ್ರ ಸರಿಪಡಿಸಲಾಗಿದೆ. ಮರುಪರಿಶೀಲನೆ ಅಗತ್ಯ.'}, 'images': {'before': '/files/r_8f3a2c/before.jpg', 'after': '/files/r_8f3a2c/after.jpg', 'after_aligned': '/files/r_8f3a2c/after_aligned.jpg', 'heatmap': '/files/r_8f3a2c/heatmap.jpg'}, 'roi': [[0.35, 0.53], [0.57, 0.53], [0.57, 0.71], [0.35, 0.71]], 'roi_source': 'marked', 'location': {'lat': 12.9352, 'lon': 77.6245, 'ward': 'Ward A'}, 'timings_ms': {'total': 2140}, 'created_at': '2026-11-01T10:42:11Z'}
@app.get("/api/health")
def health():
    return {"ok": True, "model_loaded": False, "mock_seg": os.getenv("FIXCHECK_MOCK_SEG") == "1"}
@app.get("/api/demo")
def demos():
    return []
@app.post("/api/demo/{case_id}/verify")
def demo_verify(case_id: str):
    return SAMPLE
@app.post("/api/verify")
def verify(before: UploadFile = File(...), after: UploadFile = File(...), complaint_id: str = Form(...), roi: str | None = Form(None), before_lat: float | None = Form(None), before_lon: float | None = Form(None), after_lat: float | None = Form(None), after_lon: float | None = Form(None)):
    return SAMPLE
@app.post("/api/suggest-roi")
def suggest(before: UploadFile = File(...)):
    return {"roi": None, "confidence": 0.0}
@app.get("/api/results")
def results():
    return []
@app.get("/api/results/{id}")
def result(id: str):
    raise HTTPException(404, "Result not found")
