"""Optional model advice must never influence measured repair decisions."""
import sys
from threading import Event
from types import ModuleType

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app import main, store
from backend.pipeline import config, run
from backend.pipeline.types import CheckResult, LatLon, SceneMatch
from backend.tests.test_match import textured

ROI = [[.3,.3],[.7,.3],[.7,.7],[.3,.7]]


@pytest.fixture
def advisory(monkeypatch):
    """Supply the pending module's contract without loading model weights."""
    module = ModuleType('backend.pipeline.ai_check')
    module.ai_second_opinion = lambda *args: {'status':'ok','ai_says':'repaired'}
    module.warm_up = lambda: None
    monkeypatch.setitem(sys.modules, module.__name__, module)
    return module


@pytest.fixture
def verify_pair(tmp_path, monkeypatch):
    image = textured()
    before, after = tmp_path/'before.png', tmp_path/'after.png'
    assert cv2.imwrite(str(before),image) and cv2.imwrite(str(after),image)
    H = np.array([[1.,0,4],[0,1,3],[0,0,1]])
    monkeypatch.setattr(run.match,'scene_match',lambda *args: SceneMatch(CheckResult('pass',inliers=100,inlier_ratio=.5),H))
    quality = CheckResult('pass','Even patch',score=.9)
    monkeypatch.setattr(run.score,'patch_quality',lambda *args:quality)
    monkeypatch.setattr(run.score,'heatmap',lambda before,*args:before.copy())

    def verify(pct=100., before_ll=LatLon(12,77), after_ll=LatLon(12,77)):
        mask = np.zeros(image.shape[:2],np.uint8)
        mask[200:250,200:250] = 255
        monkeypatch.setattr(run.score,'percent_resolved',lambda *args:(pct,2500,0,mask,mask.copy()))
        return run.verify(str(before),str(after),'advisory-test',before_ll,after_ll,ROI,[],str(tmp_path/'result'))

    return verify, image, H


@pytest.mark.parametrize('switch',['config','env'])
@pytest.mark.parametrize('pct,label',[(100.,'not repaired'),(50.,'partly repaired'),(0.,'repaired')])
def test_ai_on_off_does_not_change_verdict_or_confidence(advisory,verify_pair,monkeypatch,switch,pct,label):
    verify, _, _ = verify_pair
    called = []
    def opinion(*args):
        called.append(True)
        return {'status':'ok','ai_says':label,'confidence':.01,'verdict':'SUSPICIOUS'}
    advisory.ai_second_opinion = opinion
    monkeypatch.delenv('FIXCHECK_NO_AI',raising=False)
    monkeypatch.setattr(config,'AI_SECOND_OPINION',True)
    if switch=='config':
        monkeypatch.setattr(config,'AI_SECOND_OPINION',False)
    else:
        monkeypatch.setenv('FIXCHECK_NO_AI','1')
    baseline = verify(pct)
    assert baseline['ai_opinion'] is None and not called
    monkeypatch.setattr(config,'AI_SECOND_OPINION',True)
    monkeypatch.delenv('FIXCHECK_NO_AI',raising=False)
    enabled = verify(pct)
    for key in ('verdict','confidence','percent_resolved','reasons','explanation','checks'):
        assert enabled[key] == baseline[key]
    assert len(called)==1
    assert enabled['ai_opinion']['ai_says'] == label


@pytest.mark.parametrize('pct,label,agrees',[
    (100.,'repaired',True), (100.,'partly repaired',False),
    (50.,'partly repaired',True), (0.,'not repaired',True),
    (None,'repaired',False), (100.,'unrecognized',False),
])
def test_agreement_is_derived_without_modifying_advice(advisory,verify_pair,monkeypatch,pct,label,agrees):
    monkeypatch.delenv('FIXCHECK_NO_AI')
    original = {'status':'ok','ai_says':label,'agrees':'untrusted'}
    advisory.ai_second_opinion = lambda *args:original
    result = verify_pair[0](pct)
    assert result['ai_opinion']['agrees'] is agrees
    assert original['agrees'] == 'untrusted'


@pytest.mark.parametrize('status',['loading','unavailable',None])
def test_non_ok_advice_has_unknown_agreement(advisory,verify_pair,monkeypatch,status):
    monkeypatch.delenv('FIXCHECK_NO_AI')
    advisory.ai_second_opinion = lambda *args:{'status':status,'ai_says':'repaired'}
    assert verify_pair[0]()['ai_opinion']['agrees'] is None


@pytest.mark.parametrize('failure',['missing','runtime','none'])
def test_advice_failures_preserve_result(advisory,verify_pair,monkeypatch,failure):
    baseline = verify_pair[0]()
    monkeypatch.delenv('FIXCHECK_NO_AI')
    if failure=='missing':
        monkeypatch.setitem(sys.modules,'backend.pipeline.ai_check',None)
    elif failure=='runtime':
        def failed(*args):
            raise RuntimeError('Model unavailable')
        advisory.ai_second_opinion = failed
    else:
        advisory.ai_second_opinion = lambda *args:None
    result = verify_pair[0]()
    assert result['ai_opinion'] is None
    assert (result['verdict'],result['confidence']) == (baseline['verdict'],baseline['confidence'])


def test_failed_scene_never_calls_advice(advisory,verify_pair,monkeypatch):
    monkeypatch.delenv('FIXCHECK_NO_AI')
    def forbidden(*args):
        pytest.fail('A mismatched scene must not call the advisory model')
    advisory.ai_second_opinion = forbidden
    monkeypatch.setattr(run.match,'scene_match',lambda *args:SceneMatch(CheckResult('fail','Different scene')))
    result = verify_pair[0]()
    assert result['verdict'] == 'SUSPICIOUS' and result['ai_opinion'] is None


def test_advice_receives_aligned_pixels_after_scoring(advisory,verify_pair,monkeypatch):
    monkeypatch.delenv('FIXCHECK_NO_AI')
    verify, image, H = verify_pair
    calls = []
    quality = run.score.patch_quality
    def quality_checked(*args):
        calls.append('scored')
        return quality(*args)
    monkeypatch.setattr(run.score,'patch_quality',quality_checked)
    def opinion(before, aligned, roi):
        assert calls == ['scored']
        assert np.array_equal(before,image)
        expected = cv2.warpPerspective(image,H,(image.shape[1],image.shape[0]))
        assert np.array_equal(aligned,expected)
        assert roi == ROI
        calls.append('advised')
        return {'status':'ok','ai_says':'repaired'}
    advisory.ai_second_opinion = opinion
    result = verify()
    assert calls == ['scored','advised']
    assert 'ai_second_opinion' in result['timings_ms']


def test_passing_scene_with_location_failure_still_keeps_real_verdict(advisory,verify_pair,monkeypatch):
    monkeypatch.delenv('FIXCHECK_NO_AI')
    result = verify_pair[0](before_ll=LatLon(12,77),after_ll=LatLon(13,78))
    assert result['verdict']=='SUSPICIOUS'
    assert result['ai_opinion']['agrees'] is False


def test_warm_up_runs_in_background(advisory,tmp_path,monkeypatch):
    monkeypatch.delenv('FIXCHECK_NO_AI')
    monkeypatch.setattr(store,'DB_PATH',tmp_path/'warm.db')
    monkeypatch.setattr(main,'DEMO_DIR',tmp_path/'no-demos')
    started, release, finished = Event(), Event(), Event()
    def warm_up():
        started.set()
        release.wait(timeout=3)
        finished.set()
    advisory.warm_up = warm_up
    try:
        with TestClient(main.app) as client:
            assert started.wait(timeout=1)
            assert client.get('/api/health').status_code==200
            assert not finished.is_set()
    finally:
        release.set()
        assert finished.wait(timeout=1)


@pytest.mark.parametrize('switch',['config','env'])
def test_disabled_ai_never_starts_warm_up(advisory,tmp_path,monkeypatch,switch):
    monkeypatch.setattr(store,'DB_PATH',tmp_path/'disabled.db')
    monkeypatch.setattr(main,'DEMO_DIR',tmp_path/'no-demos')
    if switch=='config':
        monkeypatch.delenv('FIXCHECK_NO_AI')
        monkeypatch.setattr(config,'AI_SECOND_OPINION',False)
    def forbidden(*args,**kwargs):
        pytest.fail('Disabled advice must not start a background thread')
    monkeypatch.setattr(main,'Thread',forbidden)
    with TestClient(main.app) as client:
        assert client.get('/api/health').status_code==200


def test_warm_up_failure_is_optional(advisory):
    def unavailable():
        raise RuntimeError('Weights unavailable')
    advisory.warm_up = unavailable
    main._warm_up_ai()
