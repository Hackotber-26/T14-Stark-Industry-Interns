"""Bilingual explanation coverage without a model or network."""

import pytest

from backend.pipeline.explain import explain
from backend.pipeline.types import Decision


@pytest.mark.parametrize("verdict,pct,reasons", [
    ("FIXED", 95.0, []),
    ("PARTIAL", 54.0, []),
    ("NOT_FIXED", 0.0, []),
    ("SUSPICIOUS", None, ["The after photo is from a different location"]),
    ("SUSPICIOUS", None, ["Duplicate photo used for another complaint"]),
    ("NEEDS_REVIEW", None, ["No clear damage found inside the marked box"]),
])
def test_explanations_are_bilingual_and_interpolated(
    verdict: str, pct: float | None, reasons: list[str]
) -> None:
    result = explain(Decision(verdict, 0.8, reasons), pct)
    assert set(result) == {"en", "kn"}
    for text in result.values():
        assert isinstance(text, str) and text.strip()
        assert "{pct}" not in text
        assert "None" not in text
    assert any("\u0c80" <= char <= "\u0cff" for char in result["kn"])
    if verdict in {"FIXED", "PARTIAL"}:
        for text in result.values():
            assert str(int(pct)) in text
            assert "%" in text
