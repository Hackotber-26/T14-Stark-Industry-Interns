import cv2
import numpy as np
import pytest
from backend.pipeline.match import gps_check, scene_match
from backend.pipeline.types import LatLon


def textured():
    rng = np.random.default_rng(0)
    image = np.zeros((600, 800, 3), np.uint8)
    for i in range(250):
        x, y = rng.integers([0,0], [760,560])
        color = tuple(map(int, rng.integers(40,256,3)))
        cv2.rectangle(image,(x,y),(x+30,y+25),color,-1)
        cv2.circle(image,(int(x),int(y)),12,color,2)
    cv2.putText(image,'FixCheck street 123',(100,300),cv2.FONT_HERSHEY_SIMPLEX,2,(255,255,255),3)
    return image


def test_scene_geometry():
    before = textured()
    H = np.vstack([cv2.getRotationMatrix2D((400,300), 2, 1), [0,0,1]])
    H[:2,2] += [8, 6]
    after = cv2.warpPerspective(before,H,(800,600))
    result = scene_match(before, after)
    assert result.check.status == 'pass'
    corners = np.float32([[[80,80],[700,80],[700,500],[80,500]]])
    assert np.max(np.linalg.norm(cv2.perspectiveTransform(cv2.perspectiveTransform(corners,H),result.H)-corners,axis=2)) < 5


def test_unrelated():
    assert scene_match(textured(), np.random.default_rng(4).integers(0,256,(600,800,3),dtype=np.uint8)).check.status == 'fail'


@pytest.mark.parametrize('metres,status', [(10,'pass'),(50,'warn'),(200,'fail')])
def test_gps(metres,status):
    result = gps_check(LatLon(0,0),LatLon(metres/111195,0))
    assert result.status == status
    assert abs(result.distance_m-metres) < 0.1


def test_missing_gps():
    assert gps_check(None,LatLon(0,0)).status == 'skipped'
