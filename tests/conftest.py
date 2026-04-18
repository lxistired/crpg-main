import pathlib
import pytest

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

@pytest.fixture
def demo_brief() -> str:
    return (FIXTURES / "demo_brief.md").read_text(encoding="utf-8")

@pytest.fixture
def fixture_path():
    """Directory for canonical JSON fixtures."""
    return FIXTURES
