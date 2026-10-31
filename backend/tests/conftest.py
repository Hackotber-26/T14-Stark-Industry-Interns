import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


@pytest.fixture(autouse=True)
def optional_ai_disabled(monkeypatch):
    """Keep ordinary tests independent of model availability and model startup."""
    monkeypatch.setenv('FIXCHECK_NO_AI', '1')
