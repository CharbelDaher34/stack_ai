import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlmodel import Session

from main import app
from core.db import get_session, create_db_and_tables
from core.models import (
    LibraryCreate, DocumentCreate, ChunkCreateRequest,
    Library, Document, Chunk
)
from scripts.populate_db import create_sample_data
print("Starting tests...")
# Test fixtures
@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI app."""
    print("Creating test client...")
    create_db_and_tables(delete_tables=False)
    return TestClient(app)


@pytest.fixture(scope="module")
def sample_library_data() -> Dict[str, Any]:
    """Sample library data for testing."""
    return {
        "name": "Test Library",
        "written_by": "Test Author",
        "description": "A test library for API testing",
        "production_date": "2024-01-01T00:00:00"
    }


@pytest.fixture(scope="module")
def sample_document_data() -> Dict[str, Any]:
    """Sample document data for testing."""
    return {
        "name": "Test Document"
    }


@pytest.fixture(scope="module")
def sample_chunk_data() -> Dict[str, Any]:
    """Sample chunk data for testing."""
    return {
        "text": "This is a test chunk for vector search testing"
    }


# Library API Tests
class TestLibrariesAPI:
    """Test cases for the libraries API endpoints."""

    def test_create_library_success(self, test_client: TestClient, sample_library_data: Dict[str, Any]):
        """Test successful library creation."""
        response = test_client.post("/libraries/", json=sample_library_data)
        
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["name"] == sample_library_data["name"]
        assert response_data["written_by"] == sample_library_data["written_by"]
        assert response_data["description"] == sample_library_data["description"]
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data

    def test_create_library_invalid_data(self, test_client: TestClient):
        """Test library creation with invalid data."""
        invalid_data = {"name": ""}  # Missing required fields
        response = test_client.post("/libraries/", json=invalid_data)
        
        assert response.status_code == 422

    def test_get_all_libraries(self, test_client: TestClient):
        """Test retrieving all libraries."""
        response = test_client.get("/libraries/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) >= 1  # At least the one we created

    def test_get_library_by_id_success(self, test_client: TestClient, sample_library_data: Dict[str, Any]):
        """Test retrieving a specific library by ID."""
        # First create a library
        create_response = test_client.post("/libraries/", json=sample_library_data)
        library_id = create_response.json()["id"]
        
        # Then retrieve it
        response = test_client.get(f"/libraries/{library_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == library_id
        assert response_data["name"] == sample_library_data["name"]

    def test_get_library_by_id_not_found(self, test_client: TestClient):
        """Test retrieving a non-existent library."""
        non_existent_id = str(uuid.uuid4())
        response = test_client.get(f"/libraries/{non_existent_id}")
        
        assert response.status_code == 404
        assert "Library not found" in response.json()["detail"]

    def test_update_library_success(self, test_client: TestClient, sample_library_data: Dict[str, Any]):
        """Test successful library update."""
        # First create a library
        create_response = test_client.post("/libraries/", json=sample_library_data)
        library_id = create_response.json()["id"]
        
        # Update data
        updated_data = sample_library_data.copy()
        updated_data["name"] = "Updated Test Library"
        
        # Update the library
        response = test_client.put(f"/libraries/{library_id}", json=updated_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == "Updated Test Library"

    def test_update_library_not_found(self, test_client: TestClient, sample_library_data: Dict[str, Any]):
        """Test updating a non-existent library."""
        non_existent_id = str(uuid.uuid4())
        response = test_client.put(f"/libraries/{non_existent_id}", json=sample_library_data)
        
        assert response.status_code == 404

    def test_delete_library_success(self, test_client: TestClient, sample_library_data: Dict[str, Any]):
        """Test successful library deletion."""
        # First create a library
        create_response = test_client.post("/libraries/", json=sample_library_data)
        library_id = create_response.json()["id"]
        
        # Delete the library
        response = test_client.delete(f"/libraries/{library_id}")
        
        assert response.status_code == 204

    def test_delete_library_not_found(self, test_client: TestClient):
        """Test deleting a non-existent library."""
        non_existent_id = str(uuid.uuid4())
        response = test_client.delete(f"/libraries/{non_existent_id}")
        
        assert response.status_code == 404


# Document API Tests
class TestDocumentsAPI:
    """Test cases for the documents API endpoints."""

    @pytest.fixture(scope="class")
    def library_id(self, test_client: TestClient, sample_library_data: Dict[str, Any]) -> str:
        """Create a library for document tests."""
        response = test_client.post("/libraries/", json=sample_library_data)
        return response.json()["id"]

    def test_create_document_success(self, test_client: TestClient, sample_document_data: Dict[str, Any], library_id: str):
        """Test successful document creation."""
        document_data = sample_document_data.copy()
        document_data["library_id"] = library_id
        
        response = test_client.post("/documents/", json=document_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == sample_document_data["name"]
        assert response_data["library_id"] == library_id
        assert "id" in response_data

    def test_create_document_invalid_library(self, test_client: TestClient, sample_document_data: Dict[str, Any]):
        """Test document creation with invalid library ID."""
        document_data = sample_document_data.copy()
        document_data["library_id"] = str(uuid.uuid4())
        
        response = test_client.post("/documents/", json=document_data)
        
        # This might return 400 or 422 depending on validation
        assert response.status_code in [400, 422, 500]

    def test_get_all_documents(self, test_client: TestClient):
        """Test retrieving all documents."""
        response = test_client.get("/documents/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)

    def test_get_document_by_id_success(self, test_client: TestClient, sample_document_data: Dict[str, Any], library_id: str):
        """Test retrieving a specific document by ID."""
        # First create a document
        document_data = sample_document_data.copy()
        document_data["library_id"] = library_id
        create_response = test_client.post("/documents/", json=document_data)
        document_id = create_response.json()["id"]
        
        # Then retrieve it
        response = test_client.get(f"/documents/{document_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == document_id

    def test_get_document_by_id_not_found(self, test_client: TestClient):
        """Test retrieving a non-existent document."""
        non_existent_id = str(uuid.uuid4())
        response = test_client.get(f"/documents/{non_existent_id}")
        
        assert response.status_code == 404

    def test_get_documents_by_library(self, test_client: TestClient, library_id: str):
        """Test retrieving documents by library ID."""
        response = test_client.get(f"/documents/library/{library_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)

    def test_update_document_success(self, test_client: TestClient, sample_document_data: Dict[str, Any], library_id: str):
        """Test successful document update."""
        # First create a document
        document_data = sample_document_data.copy()
        document_data["library_id"] = library_id
        create_response = test_client.post("/documents/", json=document_data)
        document_id = create_response.json()["id"]
        
        # Update data
        updated_data = {"name": "Updated Test Document"}
        
        # Update the document
        response = test_client.put(f"/documents/{document_id}", json=updated_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == "Updated Test Document"

    def test_delete_document_success(self, test_client: TestClient, sample_document_data: Dict[str, Any], library_id: str):
        """Test successful document deletion."""
        # First create a document
        document_data = sample_document_data.copy()
        document_data["library_id"] = library_id
        create_response = test_client.post("/documents/", json=document_data)
        document_id = create_response.json()["id"]
        
        # Delete the document
        response = test_client.delete(f"/documents/{document_id}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    def test_delete_documents_by_library(self, test_client: TestClient, library_id: str):
        """Test deleting all documents in a library."""
        response = test_client.delete(f"/documents/library/{library_id}")
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]


# Chunk API Tests
class TestChunksAPI:
    """Test cases for the chunks API endpoints."""

    @pytest.fixture(scope="class")
    def document_setup(self, test_client: TestClient, sample_library_data: Dict[str, Any], sample_document_data: Dict[str, Any]) -> Dict[str, str]:
        """Create a library and document for chunk tests."""
        # Create library
        library_response = test_client.post("/libraries/", json=sample_library_data)
        library_id = library_response.json()["id"]
        
        # Create document
        document_data = sample_document_data.copy()
        document_data["library_id"] = library_id
        document_response = test_client.post("/documents/", json=document_data)
        document_id = document_response.json()["id"]
        
        return {"library_id": library_id, "document_id": document_id}

    def test_create_chunk_success(self, test_client: TestClient, sample_chunk_data: Dict[str, Any], document_setup: Dict[str, str]):
        """Test successful chunk creation."""
        chunk_data = sample_chunk_data.copy()
        chunk_data["document_id"] = document_setup["document_id"]
        
        response = test_client.post("/chunks/", json=chunk_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["text"] == sample_chunk_data["text"]
        assert response_data["document_id"] == document_setup["document_id"]
        assert "id" in response_data
        assert "embedding" in response_data
        assert isinstance(response_data["embedding"], list)

    def test_create_random_chunk(self, test_client: TestClient):
        """Test creating a random chunk."""
        response = test_client.post("/chunks/random", params={"text": "Random test chunk"})
        
        assert response.status_code == 200
        assert response.json() == "Added"

    def test_get_all_chunks(self, test_client: TestClient):
        """Test retrieving all chunks."""
        response = test_client.get("/chunks/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)

    def test_get_chunk_by_id_success(self, test_client: TestClient, sample_chunk_data: Dict[str, Any], document_setup: Dict[str, str]):
        """Test retrieving a specific chunk by ID."""
        # First create a chunk
        chunk_data = sample_chunk_data.copy()
        chunk_data["document_id"] = document_setup["document_id"]
        create_response = test_client.post("/chunks/", json=chunk_data)
        chunk_id = create_response.json()["id"]
        
        # Then retrieve it
        response = test_client.get(f"/chunks/{chunk_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == chunk_id

    def test_get_chunk_by_id_not_found(self, test_client: TestClient):
        """Test retrieving a non-existent chunk."""
        non_existent_id = str(uuid.uuid4())
        response = test_client.get(f"/chunks/{non_existent_id}")
        
        assert response.status_code == 404

    def test_get_chunks_by_document(self, test_client: TestClient, document_setup: Dict[str, str]):
        """Test retrieving chunks by document ID."""
        response = test_client.get(f"/chunks/document/{document_setup['document_id']}")
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)

    def test_update_chunk_success(self, test_client: TestClient, sample_chunk_data: Dict[str, Any], document_setup: Dict[str, str]):
        """Test successful chunk update."""
        # First create a chunk
        chunk_data = sample_chunk_data.copy()
        chunk_data["document_id"] = document_setup["document_id"]
        create_response = test_client.post("/chunks/", json=chunk_data)
        chunk_id = create_response.json()["id"]
        
        # Update data
        updated_data = {"text": "Updated test chunk text"}
        
        # Update the chunk
        response = test_client.put(f"/chunks/{chunk_id}", json=updated_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["text"] == "Updated test chunk text"

    def test_delete_chunk_success(self, test_client: TestClient, sample_chunk_data: Dict[str, Any], document_setup: Dict[str, str]):
        """Test successful chunk deletion."""
        # First create a chunk
        chunk_data = sample_chunk_data.copy()
        chunk_data["document_id"] = document_setup["document_id"]
        create_response = test_client.post("/chunks/", json=chunk_data)
        chunk_id = create_response.json()["id"]
        
        # Delete the chunk
        response = test_client.delete(f"/chunks/{chunk_id}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    def test_delete_chunks_by_document(self, test_client: TestClient, document_setup: Dict[str, str]):
        """Test deleting all chunks in a document."""
        response = test_client.delete(f"/chunks/document/{document_setup['document_id']}")
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]

    def test_search_chunks_success(self, test_client: TestClient, sample_chunk_data: Dict[str, Any], document_setup: Dict[str, str]):
        """Test chunk search functionality."""
        # First create a chunk to search for
        chunk_data = sample_chunk_data.copy()
        chunk_data["document_id"] = document_setup["document_id"]
        test_client.post("/chunks/", json=chunk_data)
        
        # Search for chunks
        search_params = {
            "query": "test chunk",
            "k": 5,
            "index_types": ["linear", "ball_tree"]
        }
        response = test_client.post("/chunks/search", params=search_params)
        
        assert response.status_code == 200
        response_data = response.json()
        assert "list_of_chunks" in response_data
        assert isinstance(response_data["list_of_chunks"], dict)
        
        # Check that both index types are present
        for index_type in ["linear", "ball_tree"]:
            assert index_type in response_data["list_of_chunks"]
            assert isinstance(response_data["list_of_chunks"][index_type], list)

    def test_search_chunks_with_pagination(self, test_client: TestClient):
        """Test chunk search with pagination parameters."""
        search_params = {
            "query": "test",
            "k": 2,
            "index_types": ["linear"]
        }
        response = test_client.post("/chunks/search", params=search_params)
        
        assert response.status_code == 200
        response_data = response.json()
        assert "list_of_chunks" in response_data


# Integration Tests
class TestAPIIntegration:
    """Integration tests for the complete API workflow."""

    def test_complete_workflow(self, test_client: TestClient, sample_library_data: Dict[str, Any], sample_document_data: Dict[str, Any], sample_chunk_data: Dict[str, Any]):
        """Test the complete workflow: create library -> document -> chunk -> search."""
        # 1. Create library
        library_response = test_client.post("/libraries/", json=sample_library_data)
        assert library_response.status_code == 201
        library_id = library_response.json()["id"]
        
        # 2. Create document
        document_data = sample_document_data.copy()
        document_data["library_id"] = library_id
        document_response = test_client.post("/documents/", json=document_data)
        assert document_response.status_code == 200
        document_id = document_response.json()["id"]
        
        # 3. Create chunk
        chunk_data = sample_chunk_data.copy()
        chunk_data["document_id"] = document_id
        chunk_response = test_client.post("/chunks/", json=chunk_data)
        assert chunk_response.status_code == 200
        chunk_id = chunk_response.json()["id"]
        
        # 4. Search chunks
        search_response = test_client.post("/chunks/search", params={"query": "test", "k": 1})
        assert search_response.status_code == 200
        
        # 5. Verify relationships
        # Get document and verify it belongs to library
        doc_check = test_client.get(f"/documents/{document_id}")
        assert doc_check.json()["library_id"] == library_id
        
        # Get chunk and verify it belongs to document
        chunk_check = test_client.get(f"/chunks/{chunk_id}")
        assert chunk_check.json()["document_id"] == document_id

    def test_cascade_deletion(self, test_client: TestClient, sample_library_data: Dict[str, Any], sample_document_data: Dict[str, Any], sample_chunk_data: Dict[str, Any]):
        """Test that deleting a library cascades to documents and chunks."""
        # Create the full hierarchy
        library_response = test_client.post("/libraries/", json=sample_library_data)
        library_id = library_response.json()["id"]
        
        document_data = sample_document_data.copy()
        document_data["library_id"] = library_id
        document_response = test_client.post("/documents/", json=document_data)
        document_id = document_response.json()["id"]
        
        chunk_data = sample_chunk_data.copy()
        chunk_data["document_id"] = document_id
        chunk_response = test_client.post("/chunks/", json=chunk_data)
        chunk_id = chunk_response.json()["id"]
        
        # Delete the library
        delete_response = test_client.delete(f"/libraries/{library_id}")
        assert delete_response.status_code == 204
        
        # Verify that document and chunk are also deleted
        doc_check = test_client.get(f"/documents/{document_id}")
        assert doc_check.status_code == 404
        
        chunk_check = test_client.get(f"/chunks/{chunk_id}")
        assert chunk_check.status_code == 404


# Health Check Test
def test_health_check(test_client: TestClient):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
