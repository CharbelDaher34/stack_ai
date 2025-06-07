"""
Vector Database API Client SDK

A Python SDK for interacting with the Vector Database API.
Provides easy-to-use methods for managing libraries, documents, and chunks,
as well as performing vector searches.
"""

import uuid
import requests
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class IndexType(Enum):
    """Available index types for vector search."""
    LINEAR = "linear"
    BALL_TREE = "ball_tree"


@dataclass
class LibraryData:
    """Data class for library information."""
    name: str
    written_by: str
    description: str
    production_date: Union[str, datetime]
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class DocumentData:
    """Data class for document information."""
    name: str
    library_id: str
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ChunkData:
    """Data class for chunk information."""
    text: str
    document_id: str
    id: Optional[str] = None
    embedding: Optional[List[float]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class SearchResult:
    """Data class for search results."""
    list_of_chunks: Dict[str, List[str]]


class VectorDBAPIError(Exception):
    """Custom exception for API errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class VectorDBClient:
    """
    Python SDK client for the Vector Database API.
    
    Provides methods to interact with libraries, documents, chunks,
    and perform vector searches.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize the Vector Database client.
        
        Args:
            base_url: Base URL of the API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict = None, 
        params: Dict = None,
        expected_status: Union[int, List[int]] = 200
    ) -> requests.Response:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: JSON data for request body
            params: Query parameters
            expected_status: Expected status code(s)
            
        Returns:
            Response object
            
        Raises:
            VectorDBAPIError: If request fails or returns unexpected status
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            # Check if status code is expected
            if isinstance(expected_status, int):
                expected_status = [expected_status]
                
            if response.status_code not in expected_status:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', f'HTTP {response.status_code}')
                except:
                    error_message = f'HTTP {response.status_code}: {response.text}'
                    error_data = {}
                
                raise VectorDBAPIError(
                    message=error_message,
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise VectorDBAPIError(f"Request failed: {str(e)}")
    
    def health_check(self) -> Dict[str, str]:
        """
        Check API health status.
        
        Returns:
            Health status dictionary
        """
        response = self._make_request("GET", "/health")
        return response.json()
    
    # Library Methods
    def create_library(
        self, 
        name: str, 
        written_by: str, 
        description: str, 
        production_date: Union[str, datetime]
    ) -> LibraryData:
        """
        Create a new library.
        
        Args:
            name: Library name
            written_by: Author name
            description: Library description
            production_date: Production date (ISO format string or datetime)
            
        Returns:
            Created library data
        """
        if isinstance(production_date, datetime):
            production_date = production_date.isoformat()
            
        data = {
            "name": name,
            "written_by": written_by,
            "description": description,
            "production_date": production_date
        }
        
        response = self._make_request("POST", "/libraries/", data=data, expected_status=201)
        result = response.json()
        
        return LibraryData(**result)
    
    def get_library(self, library_id: str) -> LibraryData:
        """
        Get a library by ID.
        
        Args:
            library_id: Library UUID
            
        Returns:
            Library data
        """
        response = self._make_request("GET", f"/libraries/{library_id}")
        result = response.json()
        
        return LibraryData(**result)
    
    def get_all_libraries(self, skip: int = 0, limit: int = 100) -> List[LibraryData]:
        """
        Get all libraries with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of library data
        """
        params = {"skip": skip, "limit": limit}
        response = self._make_request("GET", "/libraries/", params=params)
        results = response.json()
        
        return [LibraryData(**lib) for lib in results]
    
    def update_library(
        self, 
        library_id: str, 
        name: str = None, 
        written_by: str = None, 
        description: str = None, 
        production_date: Union[str, datetime] = None
    ) -> LibraryData:
        """
        Update a library.
        
        Args:
            library_id: Library UUID
            name: New library name (optional)
            written_by: New author name (optional)
            description: New description (optional)
            production_date: New production date (optional)
            
        Returns:
            Updated library data
        """
        # Get current library data
        current_library = self.get_library(library_id)
        
        # Prepare update data with current values as defaults
        data = {
            "name": name or current_library.name,
            "written_by": written_by or current_library.written_by,
            "description": description or current_library.description,
            "production_date": production_date or current_library.production_date
        }
        
        if isinstance(data["production_date"], datetime):
            data["production_date"] = data["production_date"].isoformat()
        
        response = self._make_request("PUT", f"/libraries/{library_id}", data=data)
        result = response.json()
        
        return LibraryData(**result)
    
    def delete_library(self, library_id: str) -> bool:
        """
        Delete a library and all its associated documents and chunks.
        
        Args:
            library_id: Library UUID
            
        Returns:
            True if deletion was successful
        """
        self._make_request("DELETE", f"/libraries/{library_id}", expected_status=204)
        return True
    
    # Document Methods
    def create_document(self, name: str, library_id: str) -> DocumentData:
        """
        Create a new document.
        
        Args:
            name: Document name
            library_id: Parent library UUID
            
        Returns:
            Created document data
        """
        data = {
            "name": name,
            "library_id": library_id
        }
        
        response = self._make_request("POST", "/documents/", data=data)
        result = response.json()
        
        return DocumentData(**result)
    
    def get_document(self, document_id: str) -> DocumentData:
        """
        Get a document by ID.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Document data
        """
        response = self._make_request("GET", f"/documents/{document_id}")
        result = response.json()
        
        return DocumentData(**result)
    
    def get_all_documents(self, skip: int = 0, limit: int = 100) -> List[DocumentData]:
        """
        Get all documents with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of document data
        """
        params = {"skip": skip, "limit": limit}
        response = self._make_request("GET", "/documents/", params=params)
        results = response.json()
        
        return [DocumentData(**doc) for doc in results]
    
    def get_documents_by_library(
        self, 
        library_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DocumentData]:
        """
        Get all documents in a library.
        
        Args:
            library_id: Library UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of document data
        """
        params = {"skip": skip, "limit": limit}
        response = self._make_request("GET", f"/documents/library/{library_id}", params=params)
        results = response.json()
        
        return [DocumentData(**doc) for doc in results]
    
    def update_document(self, document_id: str, name: str = None) -> DocumentData:
        """
        Update a document.
        
        Args:
            document_id: Document UUID
            name: New document name (optional)
            
        Returns:
            Updated document data
        """
        data = {}
        if name is not None:
            data["name"] = name
        
        response = self._make_request("PUT", f"/documents/{document_id}", data=data)
        result = response.json()
        
        return DocumentData(**result)
    
    def delete_document(self, document_id: str) -> Dict[str, str]:
        """
        Delete a document and all its chunks.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Deletion confirmation message
        """
        response = self._make_request("DELETE", f"/documents/{document_id}")
        return response.json()
    
    def delete_documents_by_library(self, library_id: str) -> Dict[str, str]:
        """
        Delete all documents in a library.
        
        Args:
            library_id: Library UUID
            
        Returns:
            Deletion confirmation message
        """
        response = self._make_request("DELETE", f"/documents/library/{library_id}")
        return response.json()
    
    # Chunk Methods
    def create_chunk(self, text: str, document_id: str) -> ChunkData:
        """
        Create a new chunk with automatic embedding generation.
        
        Args:
            text: Chunk text content
            document_id: Parent document UUID
            
        Returns:
            Created chunk data with embedding
        """
        data = {
            "text": text,
            "document_id": document_id
        }
        
        response = self._make_request("POST", "/chunks/", data=data)
        result = response.json()
        
        return ChunkData(**result)
    
    def create_random_chunk(self, text: str) -> str:
        """
        Create a chunk with random document assignment.
        
        Args:
            text: Chunk text content
            
        Returns:
            Confirmation message
        """
        params = {"text": text}
        response = self._make_request("POST", "/chunks/random", params=params)
        return response.json()
    
    def get_chunk(self, chunk_id: str) -> ChunkData:
        """
        Get a chunk by ID.
        
        Args:
            chunk_id: Chunk UUID
            
        Returns:
            Chunk data
        """
        response = self._make_request("GET", f"/chunks/{chunk_id}")
        result = response.json()
        
        return ChunkData(**result)
    
    def get_all_chunks(self, skip: int = 0, limit: int = 100) -> List[ChunkData]:
        """
        Get all chunks with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of chunk data
        """
        params = {"skip": skip, "limit": limit}
        response = self._make_request("GET", "/chunks/", params=params)
        results = response.json()
        
        return [ChunkData(**chunk) for chunk in results]
    
    def get_chunks_by_document(
        self, 
        document_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ChunkData]:
        """
        Get all chunks in a document.
        
        Args:
            document_id: Document UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of chunk data
        """
        params = {"skip": skip, "limit": limit}
        response = self._make_request("GET", f"/chunks/document/{document_id}", params=params)
        results = response.json()
        
        return [ChunkData(**chunk) for chunk in results]
    
    def update_chunk(self, chunk_id: str, text: str = None) -> ChunkData:
        """
        Update a chunk.
        
        Args:
            chunk_id: Chunk UUID
            text: New chunk text (optional, will regenerate embedding)
            
        Returns:
            Updated chunk data
        """
        data = {}
        if text is not None:
            data["text"] = text
        
        response = self._make_request("PUT", f"/chunks/{chunk_id}", data=data)
        result = response.json()
        
        return ChunkData(**result)
    
    def delete_chunk(self, chunk_id: str) -> Dict[str, str]:
        """
        Delete a chunk.
        
        Args:
            chunk_id: Chunk UUID
            
        Returns:
            Deletion confirmation message
        """
        response = self._make_request("DELETE", f"/chunks/{chunk_id}")
        return response.json()
    
    def delete_chunks_by_document(self, document_id: str) -> Dict[str, str]:
        """
        Delete all chunks in a document.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Deletion confirmation message
        """
        response = self._make_request("DELETE", f"/chunks/document/{document_id}")
        return response.json()
    
    # Vector Search Methods
    def search_chunks(
        self, 
        query: str, 
        k: int = 10, 
        index_types: List[Union[str, IndexType]] = None
    ) -> SearchResult:
        """
        Perform k-nearest neighbor vector search on chunks.
        
        Args:
            query: Search query text
            k: Number of nearest neighbors to return
            index_types: List of index types to use for search
            
        Returns:
            Search results grouped by index type
        """
        if index_types is None:
            index_types = [IndexType.LINEAR, IndexType.BALL_TREE]
        
        # Convert IndexType enums to strings
        index_type_strings = []
        for idx_type in index_types:
            if isinstance(idx_type, IndexType):
                index_type_strings.append(idx_type.value)
            else:
                index_type_strings.append(str(idx_type))
        
        params = {
            "query": query,
            "k": k,
            "index_types": index_type_strings
        }
        
        response = self._make_request("POST", "/chunks/search", params=params)
        result = response.json()
        
        return SearchResult(**result)
    
    # Convenience Methods
    def create_complete_hierarchy(
        self, 
        library_name: str, 
        library_author: str, 
        library_description: str, 
        document_name: str, 
        chunk_texts: List[str],
        production_date: Union[str, datetime] = None
    ) -> Dict[str, Any]:
        """
        Create a complete hierarchy: library -> document -> chunks.
        
        Args:
            library_name: Name for the library
            library_author: Author of the library
            library_description: Description of the library
            document_name: Name for the document
            chunk_texts: List of text content for chunks
            production_date: Production date (defaults to current time)
            
        Returns:
            Dictionary with created library, document, and chunk data
        """
        if production_date is None:
            production_date = datetime.now()
        
        # Create library
        library = self.create_library(
            name=library_name,
            written_by=library_author,
            description=library_description,
            production_date=production_date
        )
        
        # Create document
        document = self.create_document(
            name=document_name,
            library_id=library.id
        )
        
        # Create chunks
        chunks = []
        for text in chunk_texts:
            chunk = self.create_chunk(
                text=text,
                document_id=document.id
            )
            chunks.append(chunk)
        
        return {
            "library": library,
            "document": document,
            "chunks": chunks
        }
    
    def search_and_get_details(
        self, 
        query: str, 
        k: int = 5, 
        index_type: Union[str, IndexType] = IndexType.LINEAR
    ) -> List[ChunkData]:
        """
        Search for chunks and return detailed chunk data.
        
        Args:
            query: Search query text
            k: Number of results to return
            index_type: Index type to use for search
            
        Returns:
            List of detailed chunk data for search results
        """
        # Perform search
        search_results = self.search_chunks(
            query=query, 
            k=k, 
            index_types=[index_type]
        )
        
        # Get the index type string
        if isinstance(index_type, IndexType):
            index_type_str = index_type.value
        else:
            index_type_str = str(index_type)
        
        # Extract chunk texts from search results
        chunk_texts = search_results.list_of_chunks.get(index_type_str, [])
        
        # Get all chunks and filter by text content
        # Note: This is a simplified approach. In a real implementation,
        # you might want to return chunk IDs from the search endpoint
        all_chunks = self.get_all_chunks(limit=1000)
        
        matching_chunks = []
        for chunk in all_chunks:
            if chunk.text in chunk_texts:
                matching_chunks.append(chunk)
                if len(matching_chunks) >= k:
                    break
        
        return matching_chunks


# Example usage and testing functions
def example_usage():
    """Example usage of the Vector Database SDK."""
    
    # Initialize client
    client = VectorDBClient(base_url="http://localhost:8000")
    
    try:
        # Check API health
        health = client.health_check()
        print(f"API Health: {health}")
        
        # Create a complete hierarchy
        result = client.create_complete_hierarchy(
            library_name="Example Library",
            library_author="SDK User",
            library_description="A library created via SDK",
            document_name="Example Document",
            chunk_texts=[
                "This is the first chunk about machine learning.",
                "This is the second chunk about neural networks.",
                "This is the third chunk about vector databases."
            ]
        )
        
        print(f"Created library: {result['library'].name}")
        print(f"Created document: {result['document'].name}")
        print(f"Created {len(result['chunks'])} chunks")
        
        # Perform a search
        search_results = client.search_chunks(
            query="machine learning",
            k=2,
            index_types=[IndexType.LINEAR, IndexType.BALL_TREE]
        )
        
        print(f"Search results: {search_results.list_of_chunks}")
        
        # Get detailed search results
        detailed_results = client.search_and_get_details(
            query="neural networks",
            k=1,
            index_type=IndexType.LINEAR
        )
        
        for chunk in detailed_results:
            print(f"Found chunk: {chunk.text[:50]}...")
        
    except VectorDBAPIError as e:
        print(f"API Error: {e.message} (Status: {e.status_code})")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    example_usage() 