import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from main import app
from core.db import get_session,engine
from core.models import Library, Document, Chunk



@pytest.fixture(scope="module")
def test_create_library(client: TestClient):
    response = client.post(
        "/libraries/",
        json={"name": "Test Library", "written_by": "Test Author", "description": "A test library", "production_date": "2023-01-01T00:00:00"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Test Library"
    assert "id" in data

def test_read_libraries(client: TestClient):
    response = client.get("/libraries/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list) 