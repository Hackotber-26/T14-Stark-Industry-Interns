import numpy as np
from PIL import Image
from backend.pipeline.dedupe import phash_hex, hamming, find_duplicate
from backend.pipeline.exif import read_gps


def test_duplicate():
    image = np.random.default_rng(0).integers(0,256,(100,100,3),dtype=np.uint8)
    value = phash_hex(image)
    assert hamming(value,phash_hex(image.copy())) == 0
    result = find_duplicate(value,[('other',value)],'current')
    assert result.status == 'fail' and result.matched_complaint_id == 'other'
    assert find_duplicate(value,[('current',value)],'current').status == 'pass'
    assert find_duplicate('0'*16,[('other','f'*16)],'current').status == 'pass'


def test_missing_exif(tmp_path):
    path = tmp_path/'plain.jpg'
    Image.new('RGB',(10,10)).save(path)
    assert read_gps(str(path)) is None
    assert read_gps(str(tmp_path/'missing')) is None
