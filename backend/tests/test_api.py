"""API integration tests with isolated storage and pending B contracts replaced."""
import json
import re
from io import BytesIO
from PIL import Image
from types import SimpleNamespace
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from backend.app import main, store
from backend.pipeline import run
from backend.pipeline.types import Decision, CheckResult, LatLon
from backend.tests.test_match import textured

ROI = [[.3,.3],[.7,.3],[.7,.7],[.3,.7]]


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('FIXCHECK_MOCK_SEG','1')
    monkeypatch.setattr(store, 'DB_PATH', tmp_path/'test.db')
    monkeypatch.setattr(main, 'DEMO_DIR', tmp_path/'demo')
    main.DEMO_DIR.mkdir()
    monkeypatch.setattr(main, 'RUNS_DIR', tmp_path/'data/runs')
    main.RUNS_DIR.mkdir(parents=True)
    # Keep the actual static mounts aligned with isolated test output.
    for route in main.app.routes:
        if getattr(route,'path',None) == '/files':
            monkeypatch.setattr(route.app, 'directory', str(main.RUNS_DIR))
            monkeypatch.setattr(route.app, 'all_directories', [str(main.RUNS_DIR)])
    monkeypatch.setattr(run.segment, 'get_detector', lambda: SimpleNamespace(suggest_roi=lambda image:(None,0.0)))
    def measure(before, after, roi, valid):
        mask = np.zeros(before.shape[:2],np.uint8)
        mask[200:250,200:250] = 255
        return 95.0, 2500, 125, mask, np.zeros_like(mask)
    monkeypatch.setattr(run.score, 'percent_resolved', measure)
    monkeypatch.setattr(run.score, 'patch_quality', lambda *args: CheckResult('pass','Patch surface looks even',score=.9))
    monkeypatch.setattr(run.score, 'heatmap', lambda before,*args:before.copy())
    def decide(location, duplicate, scene, score):
        failed = [check.detail for check in (location,duplicate,scene) if check.status == 'fail']
        return Decision('SUSPICIOUS' if failed else 'FIXED',.9,failed or ['Repair verified'])
    monkeypatch.setattr(run.verdict, 'decide', decide)
    monkeypatch.setattr(run.explain, 'explain', lambda *args: {'en':'Repair verified','kn':'ದುರಸ್ತಿ ಪೂರ್ಣಗೊಂಡಿದೆ.'})
    with TestClient(main.app) as test_client:
        yield test_client


def upload(client, roi=ROI, image=None, **extra):
    image = textured() if image is None else image
    ok, encoded = cv2.imencode('.jpg',image)
    assert ok
    data = {'complaint_id':'test-1', **extra}
    if roi is not None:
        data['roi'] = json.dumps(roi)
    return client.post('/api/verify',data=data,files={'before':('before.jpg',encoded.tobytes(),'image/jpeg'),'after':('after.jpg',encoded.tobytes(),'image/jpeg')})


def test_health_empty_and_missing(client):
    assert client.get('/api/health').json() == {'ok':True,'model_loaded':False,'mock_seg':True}
    assert client.get('/api/demo').json() == []
    assert client.get('/api/results').json() == []
    assert client.get('/api/results/missing').status_code == 404
    assert client.post('/api/demo/missing/verify').status_code == 404


def test_upload_and_ledger(client):
    response = upload(client, before_lat='12', before_lon='77', after_lat='12', after_lon='77')
    assert response.status_code == 200, response.text
    result = response.json()
    assert result['verdict'] == 'FIXED'
    assert result['roi_source'] == 'marked' and result['roi'] == ROI
    assert result['checks']['location']['status'] == 'pass'
    assert result['checks']['scene']['status'] == 'pass'
    assert result['percent_resolved'] == 95
    assert result['timings_ms']['total'] > 0
    for url in result['images'].values():
        assert client.get(url).status_code == 200
    assert client.get('/api/results/'+result['id']).json() == result
    assert client.get('/api/results').json() == [result]
    assert store.all_hashes()[0][0] == 'test-1'
    assert not list(main.RUNS_DIR.glob('*/**/*upload'))


def test_roi_required_and_model_suggestion(client, monkeypatch):
    response = upload(client, roi=None)
    assert response.status_code == 422
    assert response.json()['detail'] == 'Mark the pothole on the before photo'
    assert list(main.RUNS_DIR.iterdir()) == []
    monkeypatch.setattr(run.segment, 'get_detector', lambda: SimpleNamespace(suggest_roi=lambda image:(ROI,.8)))
    response = upload(client, roi=None)
    assert response.status_code == 200
    assert response.json()['roi_source'] == 'model'


@pytest.mark.parametrize('box', [[],[[0,0]]*4,[[0,0],[2,0],[1,1],[0,1]],[[True,0],[1,0],[1,1],[0,1]]])
def test_invalid_roi(client,box):
    assert upload(client,roi=box).status_code == 422


def test_invalid_upload_and_gps(client):
    assert upload(client,before_lat='12').status_code == 422
    assert upload(client,before_lat='91',before_lon='77').status_code == 422
    response = client.post('/api/verify',data={'complaint_id':'x','roi':json.dumps(ROI)},files={'before':('x',b'bad'),'after':('x',b'bad')})
    assert response.status_code == 400
    assert 'JPEG or PNG' in response.json()['detail']
    assert client.post('/api/suggest-roi',files={'before':('bad',b'bad')}).status_code == 400
    assert client.post('/api/suggest-roi',files={'before':('empty',b'')}).status_code == 400


def test_suggest_roi(client):
    _, data = cv2.imencode('.jpg', textured())
    assert client.post('/api/suggest-roi',files={'before':('x.jpg',data.tobytes())}).json() == {'roi':None,'confidence':0.0}


def test_scene_failure_skips_scoring(client, monkeypatch):
    def forbidden(*args):
        raise AssertionError('Scene failure must not score')
    monkeypatch.setattr(run.score,'percent_resolved',forbidden)
    response = upload(client, roi=None, image=np.zeros((200,300,3),np.uint8))
    result = response.json()
    assert response.status_code == 200
    assert result['verdict'] == 'SUSPICIOUS'
    assert result['percent_resolved'] is None
    assert result['images']['after_aligned'] is None and result['images']['heatmap'] is None
    assert result['checks']['quality'] == {'status':'skipped','detail':'Not scored – photos do not match','distance_m':None,'inliers':None,'inlier_ratio':None,'matched_complaint_id':None,'hamming':None,'score':None}


def test_demo_registration_and_verification(client):
    folder = main.DEMO_DIR/'case_01'
    folder.mkdir()
    image = textured()
    for name in ('before','after'):
        cv2.imwrite(str(folder/f'{name}.jpg'),image)
    meta = {'case_id':'case_01','complaint_id':'demo-1','title':'Repair','expected':'FIXED','simulated':True,'ward':'Ward A','roi':ROI,'before_gps':{'lat':12,'lon':77},'after_gps':{'lat':12,'lon':77}}
    (folder/'meta.json').write_text(json.dumps(meta))
    with TestClient(main.app) as booted:
        assert store.all_hashes()[0][0] == 'demo-1'
        assert booted.get('/api/demo').json()[0]['before_url'] == '/demo-files/case_01/before.jpg'
        result = booted.post('/api/demo/case_01/verify').json()
        assert result['case_id'] == 'case_01' and result['simulated']
        assert result['location']['ward'] == 'Ward A'
        assert result['verdict'] == 'FIXED'


def test_store_order_and_hash_idempotency(client):
    for i in range(2):
        store.save_result({'id':str(i),'complaint_id':'c','verdict':'FIXED','created_at':str(i)})
    assert [row['id'] for row in store.list_results()] == ['1','0']
    store.add_hash('c','abc')
    store.add_hash('c','abc')
    assert store.all_hashes() == [('c','abc')]


@pytest.mark.parametrize('order', [('case_05', 'case_01'), ('case_01', 'case_05')])
def test_demo_duplicate_uses_earlier_cases_and_real_uploads(client, order):
    image = textured()
    for case_id in ('case_05', 'case_01'):
        folder = main.DEMO_DIR/case_id
        folder.mkdir()
        for name in ('before', 'after'):
            cv2.imwrite(str(folder/f'{name}.jpg'), image)
        # Deliberately misleading labels must not control duplicate checks.
        meta = {'case_id':case_id, 'complaint_id':case_id, 'title':'Test',
                'expected':'NOT_FIXED', 'simulated':True, 'ward':'Ward A', 'roi':ROI}
        (folder/'meta.json').write_text(json.dumps(meta))
    with TestClient(main.app) as booted:
        assert [cid for cid, _ in store.all_hashes()] == ['case_01', 'case_05']
        for case_id in order:
            result = booted.post(f'/api/demo/{case_id}/verify').json()
            assert result['checks']['duplicate']['status'] == ('pass' if case_id=='case_01' else 'fail')
        assert upload(booted).status_code == 200
        result = booted.post('/api/demo/case_01/verify').json()
        assert result['checks']['duplicate']['status'] == 'fail'
        assert result['checks']['duplicate']['matched_complaint_id'] == 'test-1'


def test_partial_split_follows_damage_bounds(monkeypatch):
    from scripts import make_demo_pairs as pairs
    image = np.zeros((100, 100, 3), np.uint8)
    damage = np.zeros((100, 100), np.uint8)
    damage[20:60, 10:30] = 255
    captured = []
    monkeypatch.setattr(pairs, 'repair_mask', lambda *args: (damage.copy(), 'defect_mask'))
    def fill(before, mask, roi, rng):
        captured.append(mask.copy())
        return before
    monkeypatch.setattr(pairs, 'fill_repair', fill)
    pairs.make_after(image, ROI, 'partial', 0)
    assert np.count_nonzero(captured[0][:, :20]) == 400
    assert not np.any(captured[0][:, 20:])


@pytest.mark.parametrize('format', ['JPEG', 'PNG'])
def test_large_phone_photos(client, format):
    photo = Image.new('RGB', (4000, 3000), (50, 100, 150))
    data = BytesIO()
    photo.save(data, format=format)
    files = {name: ('phone.'+format.lower(), data.getvalue()) for name in ('before', 'after')}
    response = client.post('/api/verify', data={'complaint_id':'phone-large', 'roi':json.dumps(ROI)}, files=files)
    assert response.status_code == 200, response.text
    saved = cv2.imread(str(main.RUNS_DIR/response.json()['id']/'before.jpg'))
    assert saved.shape == (768, 1024, 3)
    suggestion = client.post('/api/suggest-roi', files={'before':files['before']})
    assert suggestion.status_code == 200


def test_phone_orientation_matches_displayed_pixels_and_registered_hash(client, monkeypatch):
    from backend.pipeline.dedupe import phash_hex
    upright = Image.fromarray(cv2.cvtColor(textured(), cv2.COLOR_BGR2RGB))
    raw = upright.transpose(Image.Transpose.ROTATE_90)
    metadata = Image.Exif()
    metadata[274] = 6  # Stored pixels need a clockwise quarter turn for display.
    oriented, plain = BytesIO(), BytesIO()
    raw.save(oriented, format='JPEG', quality=95, exif=metadata)
    upright.save(plain, format='PNG')
    seen = []
    monkeypatch.setattr(run.segment, 'get_detector', lambda: SimpleNamespace(suggest_roi=lambda image: (seen.append(image.copy()) or ROI, .8)))
    assert client.post('/api/suggest-roi', files={'before':('phone.jpg',oriented.getvalue())}).status_code == 200
    response = client.post('/api/verify', data={'complaint_id':'phone-rotated', 'roi':json.dumps(ROI)},
                           files={'before':('phone.jpg',oriented.getvalue()), 'after':('plain.png',plain.getvalue())})
    assert response.status_code == 200, response.text
    result = response.json()
    saved = cv2.imread(str(main.RUNS_DIR/result['id']/'before.jpg'))
    assert saved.shape == seen[0].shape == (600, 800, 3)
    assert np.abs(saved.astype(float)-seen[0]).mean() < 5
    assert result['checks']['scene']['status'] == 'pass'
    # Register the oriented input as after evidence too.
    response = client.post('/api/verify', data={'complaint_id':'phone-after', 'roi':json.dumps(ROI)},
                           files={'before':('plain.png',plain.getvalue()), 'after':('phone.jpg',oriented.getvalue())})
    assert response.status_code == 200
    assert ('phone-after', phash_hex(seen[0])) in store.all_hashes()


@pytest.mark.parametrize('bad', [b'', b'not an image', b'\xff\xd8\xff\xe0' + bytes(40)])
@pytest.mark.parametrize('side', ['before', 'after'])
def test_unreadable_photos_return_400_and_leave_no_results(client, bad, side):
    valid = BytesIO()
    Image.new('RGB',(30,20)).save(valid,format='PNG')
    files = {name:('photo.png',bad if name==side else valid.getvalue()) for name in ('before','after')}
    response = client.post('/api/verify',data={'complaint_id':'broken','roi':json.dumps(ROI)},files=files)
    assert response.status_code == 400
    assert response.json()['detail'] == 'Unreadable image. Upload a valid JPEG or PNG photo.'
    assert store.list_results() == [] and store.all_hashes() == []
    assert list(main.RUNS_DIR.iterdir()) == []


@pytest.mark.parametrize('scene_matches', [True, False])
def test_report_pdf_download(client, monkeypatch, scene_matches):
    from backend.app import report
    monkeypatch.setattr(report, '_ROOT', store.DB_PATH.parent)
    response = upload(client, image=None if scene_matches else np.zeros((200,300,3),np.uint8))
    assert response.status_code == 200
    result = response.json()
    response = client.get(f'/api/results/{result["id"]}/report.pdf')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/pdf'
    assert f'{result["id"]}-report.pdf' in response.headers['content-disposition']
    assert response.content.startswith(b'%PDF-') and response.content.rstrip().endswith(b'%%EOF')
    assert len(re.findall(rb'/Type\s*/Page\b', response.content)) == 1
    assert b'/Subtype /Image' in response.content
    assert not list(main.RUNS_DIR.glob('report_*.pdf'))


def test_report_missing_result(client, monkeypatch):
    from backend.app import report
    def forbidden(*args):
        raise AssertionError('A missing result must not build a PDF')
    monkeypatch.setattr(report, 'build_report', forbidden)
    response = client.get('/api/results/missing/report.pdf')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Result not found'
    assert not list(main.RUNS_DIR.glob('*.pdf'))


def test_report_generation_failure_removes_temporary_file(client, monkeypatch):
    from backend.app import report
    result = upload(client).json()
    def failed(value, path):
        raise RuntimeError('Report generation failed')
    monkeypatch.setattr(report, 'build_report', failed)
    with pytest.raises(RuntimeError, match='Report generation failed'):
        client.get(f'/api/results/{result["id"]}/report.pdf')
    assert not list(main.RUNS_DIR.glob('report_*.pdf'))



def test_real_demo_cases_use_only_after_hashes(tmp_path, monkeypatch):
    from backend.pipeline import dedupe, exif
    monkeypatch.setenv('FIXCHECK_MOCK_SEG', '1')
    monkeypatch.setattr(store, 'DB_PATH', tmp_path/'real-demo.db')
    monkeypatch.setattr(main, 'RUNS_DIR', tmp_path/'runs')
    main.RUNS_DIR.mkdir()
    with TestClient(main.app) as real_client:
        cases = real_client.get('/api/demo').json()
        assert [case['case_id'] for case in cases] == [f'case_{index:02d}' for index in range(1,8)]
        assert [case['title'] for case in cases[-2:]] == ['Real photo: object removed', 'Real photo: different spot']
        assert not any(case['simulated'] for case in cases[-2:])
        # The same before photo is used twice, but only after evidence is indexed.
        before_hash = dedupe.phash_hex(exif.read_bgr(str(main.DEMO_DIR/'case_06/before.jpg')))
        assert all(value != before_hash for _, value in store.all_hashes())
        assert len(store.all_hashes()) == 7
        for case_id, expected in [('case_07','SUSPICIOUS'), ('case_06','FIXED')]:
            response = real_client.post(f'/api/demo/{case_id}/verify')
            assert response.status_code == 200, response.text
            result = response.json()
            assert result['verdict'] == expected, result
            assert result['simulated'] is False
            assert result['checks']['location']['status'] == 'skipped'
            assert result['checks']['duplicate']['status'] == 'pass'
            assert result['location']['lat'] is None and result['location']['lon'] is None
            assert result['roi'] == [[0.39,0.40],[0.56,0.40],[0.56,0.51],[0.39,0.51]]
