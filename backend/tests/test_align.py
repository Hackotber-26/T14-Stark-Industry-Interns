import numpy as np
from backend.pipeline.align import resize_max_side, warp_after_to_before, valid_region_mask


def test_resize():
    assert resize_max_side(np.zeros((1200,1600,3),np.uint8)).shape == (768,1024,3)


def test_translation():
    image = np.full((20,30,3),100,np.uint8)
    H = np.array([[1.,0,5],[0,1,3],[0,0,1]])
    warped = warp_after_to_before(image,H,image.shape)
    mask = valid_region_mask(image.shape,H,image.shape)
    assert np.all(warped[3:,5:] == 100)
    assert np.all(mask[:3] == 0)
    assert np.count_nonzero(mask) == 17*25
