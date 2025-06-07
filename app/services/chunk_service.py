import uuid
import math
from typing import List, Optional, Tuple, Dict, Any, Union
from datetime import datetime,timezone
from sqlmodel import Session
from infrastructure.repositories.chunk_repository import ChunkRepository
from core.models.chunk_model import Chunk, ChunkCreate, ChunkUpdate, ChunkCreateRequest
from infrastructure.indexing.linear_index import LinearIndex
from infrastructure.indexing.kd_tree import KDTreeIndex
from sentence_transformers import SentenceTransformer
from cohere import Client
from fastapi import HTTPException
class ChunkService:
    def __init__(self, session: Session):
        self.chunk_repository = ChunkRepository(session)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
    def create_chunk(self, chunk_create: ChunkCreateRequest,random_chunk:bool=False) -> Chunk:
        """Create a new chunk with business logic validation."""
        # Business logic: validate that document exists could go here
        # Validate embedding dimension consistency could go here
        embedding = self.model.encode(chunk_create.text)
        if not random_chunk:
            chunk_create=ChunkCreate(text=chunk_create.text,document_id=chunk_create.document_id,embedding=embedding.tolist())
        else:
            #get random document id
            document_id=self.chunk_repository.get_random_document_id()
            chunk_create=ChunkCreate(text=chunk_create.text,document_id=document_id,embedding=embedding.tolist())
        db_chunk = Chunk.model_validate(chunk_create)
        
        return self.chunk_repository.create(db_chunk)

    def get_chunk(self, chunk_id: uuid.UUID) -> Optional[Chunk]:
        """Get a chunk by its ID."""
        chunk=self.chunk_repository.get(chunk_id)
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        return chunk

    def get_chunks_by_document(self, document_id: uuid.UUID, skip: int = 0, limit: int = 100, for_indexing: bool = False) -> List[Chunk]:
        """Get all chunks in a specific document."""
        
        return self.chunk_repository.get_by_document_id(document_id, skip=skip, limit=limit, for_indexing=for_indexing)

    def get_all_chunks(self, skip: int = 0, limit: int = 100, for_indexing: bool = False) -> List[Chunk]:
        """Get all chunks with pagination."""
        return self.chunk_repository.get_all(skip=skip, limit=limit, for_indexing=for_indexing)

    def update_chunk(self, chunk_id: uuid.UUID, chunk_update: ChunkUpdate) -> Optional[Chunk]:
        """Update a chunk with business logic."""
        db_chunk = self.chunk_repository.get(chunk_id)
        if not db_chunk:
            raise HTTPException(status_code=404, detail="Chunk not found, it canot be")
        
        # Update only provided fields
        update_data = chunk_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_chunk, key, value)
        
        # Update timestamp
        db_chunk.updated_at = datetime.now(timezone.utc)
        
        return self.chunk_repository.update(db_chunk)

    def delete_chunk(self, chunk_id: uuid.UUID) -> bool:
        """Delete a chunk."""
        return self.chunk_repository.delete(chunk_id)

    def delete_chunks_by_document(self, document_id: uuid.UUID) -> int:
        """Delete all chunks in a document."""
        return self.chunk_repository.delete_by_document_id(document_id)
    
    def get_random_document_id(self) -> uuid.UUID:
        return self.chunk_repository.get_random_document_id()