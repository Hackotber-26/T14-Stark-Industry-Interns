"""Automatic boxes ignore lighting-only changes and invalid warped pixels."""
import cv2
import numpy as np
from backend.pipeline.run import auto_change_roi


def road():
    return np.random.default_rng(0).integers(70,150,(400,600,3),dtype=np.uint8)


def test_identical_and_global_lighting_have_no_region():
    image = road()
    valid = np.full(image.shape[:2],255,np.uint8)
    assert auto_change_roi(image,image,valid) is None
    brighter = np.clip(image.astype(float)*1.1+5,0,255).astype(np.uint8)
    assert auto_change_roi(image,brighter,valid) is None


def test_invalid_warp_border_is_not_a_change():
    image = road()
    after = image.copy()
    after[:100] = 0
    valid = np.full(image.shape[:2],255,np.uint8)
    valid[:100] = 0
    assert auto_change_roi(image,after,valid) is None
    assert auto_change_roi(image,after,np.zeros_like(valid)) is None


def test_tiny_region_is_ignored():
    image = road()
    after = image.copy()
    after[200:210,200:210] = 240
    valid = np.full(image.shape[:2],255,np.uint8)
    assert auto_change_roi(image,after,valid) is None


def test_largest_change_is_padded_and_normalized():
    image = road()
    after = image.copy()
    after[150:220,200:290] = 240
    after[300:320,400:420] = 240
    valid = np.full(image.shape[:2],255,np.uint8)
    roi = auto_change_roi(image,after,valid)
    assert roi is not None
    assert roi[0][0] < 200/600 and roi[2][0] > 290/600
    assert roi[0][1] < 150/400 and roi[2][1] > 220/400
    assert all(0<=value<=1 for point in roi for value in point)
