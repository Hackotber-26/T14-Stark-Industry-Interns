"""Optional AI behavior without loading weights or using the network."""
import numpy as np
import pytest

from backend.pipeline import ai_check


@pytest.fixture(autouse=True)
def isolated_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai_check, '_model', None)
    monkeypatch.setattr(ai_check, '_processor', None)
    monkeypatch.setattr(ai_check, '_device', None)
    monkeypatch.setattr(ai_check, '_attempted', False)


@pytest.fixture
def pair() -> tuple:
    image = np.zeros((100, 200, 3), np.uint8)
    roi = [[0.25, 0.25], [0.75, 0.25], [0.75, 0.75], [0.25, 0.75]]
    return image, image.copy(), roi


def test_unavailable_model_is_attempted_once(monkeypatch, pair) -> None:
    calls = []

    def unavailable():
        calls.append(True)
        raise OSError('No cached weights')

    monkeypatch.setattr(ai_check, '_load_model', unavailable)
    assert ai_check.warm_up() is None
    assert ai_check.ai_second_opinion(*pair) is None
    assert ai_check.ai_second_opinion(*pair) is None
    assert len(calls) == 1


@pytest.mark.parametrize('before,after,says', [
    (0.9, 0.2, 'repaired'), (0.9, 0.6, 'not repaired'),
    (0.9, 0.8, 'not repaired'), (0.8, 0.5, 'partly repaired'),
    (0.6, 0.4, 'partly repaired'), (0.5, 0.2, 'repaired'),
    (0.876, 0.234, 'repaired'),
])
def test_output_shape_and_rules(monkeypatch, pair, before, after, says) -> None:
    monkeypatch.setattr(ai_check, '_load_model', lambda: (object(), object(), 'cpu'))
    scores = iter([before, after])
    crops = []

    def probability(crop):
        crops.append(crop)
        return next(scores)

    monkeypatch.setattr(ai_check, '_damage_probability', probability)
    assert ai_check.ai_second_opinion(*pair) == {
        'status': 'ok', 'damage_before': round(before, 2),
        'damage_after': round(after, 2), 'ai_says': says}
    assert len(crops) == 2
    assert all(crop.shape == (66, 130, 3) for crop in crops)


def test_no_damage_skips_after_inference(monkeypatch, pair) -> None:
    monkeypatch.setattr(ai_check, '_load_model', lambda: (object(), object(), 'cpu'))
    calls = []

    def probability(crop):
        calls.append(True)
        return 0.074

    monkeypatch.setattr(ai_check, '_damage_probability', probability)
    assert ai_check.ai_second_opinion(*pair) == {
        'status': 'no_damage_recognised', 'damage_before': 0.07,
        'damage_after': None, 'ai_says': None}
    assert len(calls) == 1


def test_inference_failure_is_optional(monkeypatch, pair) -> None:
    monkeypatch.setattr(ai_check, '_load_model', lambda: (object(), object(), 'cpu'))

    def fail(crop):
        raise RuntimeError('Device unavailable')

    monkeypatch.setattr(ai_check, '_damage_probability', fail)
    assert ai_check.ai_second_opinion(*pair) is None


def test_invalid_roi_is_optional(monkeypatch, pair) -> None:
    monkeypatch.setattr(ai_check, '_load_model', lambda: (object(), object(), 'cpu'))
    assert ai_check.ai_second_opinion(pair[0], pair[1], []) is None
