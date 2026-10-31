"""Verdict precedence, thresholds, and confidence from SPEC section 7."""

import pytest

from backend.pipeline.config import FIXED_MIN_PCT, PARTIAL_MIN_PCT
from backend.pipeline.types import CheckResult, ScoreResult
from backend.pipeline.verdict import decide


def make_score(pct: float | None, quality: str = "pass") -> ScoreResult:
    return ScoreResult(pct, 1000, 100, CheckResult(status=quality))


def assert_decision(result, verdict: str) -> None:
    assert result.verdict == verdict
    assert 0.30 <= result.confidence <= 0.99
    assert result.confidence == round(result.confidence, 2)
    assert result.reasons
    assert all(isinstance(reason, str) and reason.strip() for reason in result.reasons)


@pytest.mark.parametrize("pct,quality,expected", [
    (100.0, "pass", "FIXED"),
    (FIXED_MIN_PCT, "pass", "FIXED"),
    (FIXED_MIN_PCT, "warn", "FIXED"),
    (FIXED_MIN_PCT, "fail", "PARTIAL"),
    (FIXED_MIN_PCT - 0.1, "pass", "PARTIAL"),
    (PARTIAL_MIN_PCT, "pass", "PARTIAL"),
    (PARTIAL_MIN_PCT, "fail", "PARTIAL"),
    (PARTIAL_MIN_PCT - 0.1, "pass", "NOT_FIXED"),
    (0.0, "pass", "NOT_FIXED"),
    (None, "pass", "NEEDS_REVIEW"),
])
def test_verdict_table(pct: float | None, quality: str, expected: str) -> None:
    result = decide(CheckResult("pass"), CheckResult("pass"),
                    CheckResult("pass", inlier_ratio=0.5), make_score(pct, quality))
    assert_decision(result, expected)
    if quality == "fail" and pct is not None and pct >= FIXED_MIN_PCT:
        assert any("patch quality looks poor" in reason.lower() for reason in result.reasons)


def test_missing_score_needs_review() -> None:
    result = decide(CheckResult("pass"), CheckResult("pass"), CheckResult("pass"), None)
    assert_decision(result, "NEEDS_REVIEW")
    assert any("no clear damage found inside the marked box" in reason.lower()
               for reason in result.reasons)


@pytest.mark.parametrize("failed", [(0,), (1,), (2,), (0, 1, 2)])
@pytest.mark.parametrize("score", [None, make_score(None), make_score(100)])
def test_failed_checks_take_priority(failed: tuple, score: ScoreResult | None) -> None:
    names = ["location", "duplicate", "scene"]
    checks = [CheckResult("fail" if i in failed else "pass",
                          detail=f"{name} check failed" if i in failed else "",
                          inlier_ratio=0.5 if i == 2 else None)
              for i, name in enumerate(names)]
    result = decide(*checks, score)
    assert_decision(result, "SUSPICIOUS")
    assert len(result.reasons) >= len(failed)


@pytest.mark.parametrize("location,pct,quality,ratio", [
    ("pass", 100.0, "pass", 0.5),
    ("skipped", 100.0, "pass", 0.5),
    ("warn", 100.0, "pass", 0.5),
    ("pass", FIXED_MIN_PCT, "pass", 0.5),
    ("pass", PARTIAL_MIN_PCT, "pass", 0.5),
    ("pass", 100.0, "warn", 0.5),
    ("pass", 100.0, "pass", 0.25),
    ("pass", 100.0, "pass", 0.8),
    ("skipped", PARTIAL_MIN_PCT, "warn", 0.25),
])
def test_confidence_formula(location: str, pct: float, quality: str, ratio: float) -> None:
    expected = 0.92
    expected -= {"skipped": 0.15, "warn": 0.10}.get(location, 0)
    if min(abs(pct - FIXED_MIN_PCT), abs(pct - PARTIAL_MIN_PCT)) <= 7:
        expected -= 0.15
    if quality == "warn":
        expected -= 0.10
    expected *= 0.85 + 0.15 * min(ratio / 0.5, 1)
    expected = round(max(0.30, min(0.99, expected)), 2)
    result = decide(CheckResult(location), CheckResult("pass"),
                    CheckResult("pass", inlier_ratio=ratio), make_score(pct, quality))
    assert result.confidence == expected
