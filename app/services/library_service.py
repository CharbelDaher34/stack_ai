import uuid
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session
from infrastructure.repositories.library_repository import LibraryRepository
from core.models import Library, LibraryCreate, LibraryRead # Assuming LibraryUpdate will be similar to LibraryCreate
from core.db import get_session # To be used with FastAPI Depends

class LibraryService:
    def __init__(self, session: Session):
        self.repository = LibraryRepository(session)

    def create_library(self, library_create: LibraryCreate) -> Library:
        """Create a new library with business logic validation."""
        # Business logic: check for duplicate names, validate input, etc.
        return self.repository.create_library(library_create)

    def get_library(self, library_id: uuid.UUID) -> Optional[Library]:
        """Get a library by its ID."""
        return self.repository.get_library(library_id)

    def get_libraries(self, skip: int = 0, limit: int = 100) -> List[Library]:
        """Get all libraries with pagination."""
        return self.repository.get_libraries(skip=skip, limit=limit)

    def update_library(self, library_id: uuid.UUID, library_update_data: LibraryCreate) -> Optional[Library]:
        """Update a library with business logic validation."""
        return self.repository.update_library(library_id, library_update_data)

    def delete_library(self, library_id: uuid.UUID) -> Optional[Library]:
        """
        Delete a library and all its associated documents and chunks.
        This is a cascade delete operation.
        """
        # Get the library first to ensure it exists
        library = self.repository.get_library(library_id)
        if not library:
            return None
        
        # Import here to avoid circular imports
        from services.document_service import DocumentService
        
        # Delete all documents (and their chunks) in the library
        document_service = DocumentService(self.repository.session)
        documents_deleted = document_service.delete_documents_by_library(library_id)
        
        # Delete the library
        deleted_library = self.repository.delete_library(library_id)
        
        return deleted_library

    def index_library(self, library_id: uuid.UUID) -> bool:
        """
        Mark a library as indexed.
        In a real implementation, this would trigger the indexing process.
        """
        library = self.repository.get_library(library_id)
        if not library:
            return False
        
        # Update the indexed_at timestamp
        updated_library = self.repository.update_library(
            library_id, 
            LibraryCreate(name=library.name),
            indexed_at=datetime.utcnow()
        )
        
        return updated_library is not None

    def is_library_indexed(self, library_id: uuid.UUID) -> bool:
        """Check if a library has been indexed."""
        library = self.repository.get_library(library_id)
        if not library:
            return False
        
        return library.indexed_at is not None

    def get_library_stats(self, library_id: uuid.UUID) -> Optional[dict]:
        """Get statistics about a library (document count, chunk count, etc.)."""
        library = self.repository.get_library(library_id)
        if not library:
            return None
        
        # Import here to avoid circular imports
        from services.document_service import DocumentService
        from services.chunk_service import ChunkService
        
        document_service = DocumentService(self.repository.session)
        chunk_service = ChunkService(self.repository.session)
        
        # Get all documents in the library
        documents = document_service.get_documents_by_library(library_id)
        document_count = len(documents)
        
        # Count total chunks across all documents
        total_chunks = 0
        for document in documents:
            chunks = chunk_service.get_chunks_by_document(document.id)
            total_chunks += len(chunks)
        
        return {
            "library_id": library_id,
            "library_name": library.name,
            "document_count": document_count,
            "chunk_count": total_chunks,
            "created_at": library.created_at,
            "updated_at": library.updated_at,
        } 