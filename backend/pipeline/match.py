"""Location and feature-based scene checks."""
import math
import cv2
import numpy as np
from . import config as c
from .types import LatLon, CheckResult, SceneMatch


def haversine_m(a: LatLon, b: LatLon) -> float:
    """Return great-circle distance in metres."""
    p, q = math.radians(a.lat), math.radians(b.lat)
    d = math.sin((q-p)/2)**2 + math.cos(p)*math.cos(q)*math.sin(math.radians(b.lon-a.lon)/2)**2
    return 6371000 * 2 * math.asin(math.sqrt(min(1.0, d)))


def gps_check(before: LatLon | None, after: LatLon | None) -> CheckResult:
    """Compare GPS positions when both are available."""
    if before is None or after is None:
        return CheckResult('skipped', 'GPS unavailable')
    distance = haversine_m(before, after)
    status = 'pass' if distance <= c.GPS_PASS_M else 'warn' if distance <= c.GPS_WARN_M else 'fail'
    return CheckResult(status, f'Photos taken {distance:.0f} m apart', distance_m=distance)


def scene_match(before_bgr: np.ndarray, after_bgr: np.ndarray) -> SceneMatch:
    """Recover an after-to-before homography using SIFT and RANSAC."""
    sift = cv2.SIFT_create(nfeatures=c.SIFT_FEATURES)
    kb, db = sift.detectAndCompute(cv2.cvtColor(before_bgr, cv2.COLOR_BGR2GRAY), None)
    ka, da = sift.detectAndCompute(cv2.cvtColor(after_bgr, cv2.COLOR_BGR2GRAY), None)
    if db is None or da is None or len(db) < 2:
        return SceneMatch(CheckResult('fail', 'Not enough distinctive points'))
    pairs = cv2.BFMatcher().knnMatch(da, db, k=2)
    good = [pair[0] for pair in pairs if len(pair)==2 and pair[0].distance < c.LOWE_RATIO*pair[1].distance]
    if len(good) < c.MIN_GOOD_MATCHES:
        return SceneMatch(CheckResult('fail', 'Not enough matching points'))
    src = np.float32([ka[m.queryIdx].pt for m in good])
    dst = np.float32([kb[m.trainIdx].pt for m in good])
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, c.RANSAC_REPROJ)
    n = int(mask.sum()) if mask is not None else 0
    ratio = n / len(good)
    passed = H is not None and np.isfinite(H).all() and c.H_DET_MIN <= np.linalg.det(H[:2,:2]) <= c.H_DET_MAX and n >= c.SCENE_MIN_INLIERS and ratio >= c.SCENE_MIN_INLIER_RATIO
    return SceneMatch(CheckResult('pass' if passed else 'fail', f'{n} matching points ({ratio:.0%}) – '+('same scene' if passed else 'photos do not match'), inliers=n, inlier_ratio=ratio), H if passed else None)
