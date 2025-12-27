import pytest
from fastapi.testclient import TestClient
from api.main import app   # adjust import if needed

@pytest.fixture(scope="session")
def client():
    return TestClient(app)