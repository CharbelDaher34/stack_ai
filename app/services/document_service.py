import uuid
from typing import List, Optional, Tuple
from datetime import datetime,timezone
from sqlmodel import Session
from infrastructure.repositories.document_repository import DocumentRepository
from infrastructure.repositories.chunk_repository import ChunkRepository
from core.models import Document, DocumentCreate, DocumentUpdate
from fastapi import HTTPException
from services.library_service import LibraryService 
class DocumentService:
    def __init__(self, session: Session):
        self.document_repository = DocumentRepository(session)
        self.chunk_repository = ChunkRepository(session)
        self.library_service = LibraryService(session)
    def create_document(self, document_create: DocumentCreate) -> Document:
        """Create a new document with business logic validation."""
        # Business logic: validate that library exists could go here
        db_document = Document.model_validate(document_create)
        library = self.library_service.get_library(document_create.library_id)
        if not library:
            raise HTTPException(status_code=404, detail="Library not found")
        return self.document_repository.create(db_document)

    def get_document(self, document_id: uuid.UUID) -> Optional[Document]:
        """Get a document by its ID."""
        document=self.document_repository.get(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    def get_documents_by_library(self, library_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get all documents in a specific library."""
        return self.document_repository.get_by_library_id(library_id, skip=skip, limit=limit)

    def get_all_documents(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get all documents with pagination."""
        return self.document_repository.get_all(skip=skip, limit=limit)

    def update_document(self, document_id: uuid.UUID, document_update: DocumentUpdate) -> Optional[Document]:
        """Update a document with business logic."""
        db_document = self.document_repository.get(document_id)
        if not db_document:
            return None
        
        # Update only provided fields
        update_data = document_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_document, key, value)
        
        # Update timestamp
        db_document.updated_at = datetime.now(timezone.utc)
        
        return self.document_repository.update(db_document)

    def delete_document(self, document_id: uuid.UUID) -> bool:
        """Delete a document and all its chunks."""
        # Business logic: delete all associated chunks first
        deleted_chunks = self.chunk_repository.delete_by_document_id(document_id)
        
        # Then delete the document
        return self.document_repository.delete(document_id)

    def delete_documents_by_library(self, library_id: uuid.UUID) -> Tuple[List[uuid.UUID], List[uuid.UUID]]:
        """Delete all documents in a library and their chunks."""
        # Get all documents in the library
        documents = self.document_repository.get_by_library_id(library_id)
        
        # Delete chunks for each document
        chunks_ids_deleted=[]
        for document in documents:
            chunks_ids_deleted.extend(self.chunk_repository.delete_by_document_id(document.id))
        
        # Delete all documents in the library
        documents_ids_deleted = self.document_repository.delete_by_library_id(library_id)
        
        return chunks_ids_deleted,documents_ids_deleted
