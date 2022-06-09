import pytest


@pytest.fixture
def pytest_fixture(monkeypatch):
    pass


@pytest.fixture(scope="session")
def pytest_fixture_scoped():
    pass
