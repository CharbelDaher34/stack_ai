import uuid
import math
from typing import List, Optional, Tuple
from datetime import datetime
from sqlmodel import Session
from infrastructure.repositories.chunk_repository import ChunkRepository
from app.core.models.models import Chunk, ChunkCreate, ChunkRead, ChunkUpdate


class ChunkService:
    def __init__(self, session: Session):
        self.chunk_repository = ChunkRepository(session)

    def create_chunk(self, chunk_create: ChunkCreate) -> Chunk:
        """Create a new chunk with business logic validation."""
        # Business logic: validate that document exists could go here
        # Validate embedding dimension consistency could go here
        db_chunk = Chunk.model_validate(chunk_create)
        return self.chunk_repository.create(db_chunk)

    def get_chunk(self, chunk_id: uuid.UUID) -> Optional[Chunk]:
        """Get a chunk by its ID."""
        return self.chunk_repository.get(chunk_id)

    def get_chunks_by_document(self, document_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """Get all chunks in a specific document."""
        return self.chunk_repository.get_by_document_id(document_id, skip=skip, limit=limit)

    def get_all_chunks(self, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """Get all chunks with pagination."""
        return self.chunk_repository.get_all(skip=skip, limit=limit)

    def update_chunk(self, chunk_id: uuid.UUID, chunk_update: ChunkUpdate) -> Optional[Chunk]:
        """Update a chunk with business logic."""
        db_chunk = self.chunk_repository.get(chunk_id)
        if not db_chunk:
            return None
        
        # Update only provided fields
        update_data = chunk_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_chunk, key, value)
        
        # Update timestamp
        db_chunk.updated_at = datetime.utcnow()
        
        return self.chunk_repository.update(db_chunk)

    def delete_chunk(self, chunk_id: uuid.UUID) -> bool:
        """Delete a chunk."""
        return self.chunk_repository.delete(chunk_id)

    def delete_chunks_by_document(self, document_id: uuid.UUID) -> int:
        """Delete all chunks in a document."""
        return self.chunk_repository.delete_by_document_id(document_id)

    # Vector similarity search methods
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    def euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

    def manhattan_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate Manhattan distance between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same dimension")
        
        return sum(abs(a - b) for a, b in zip(vec1, vec2))

    def knn_search(
        self, 
        query_embedding: List[float], 
        k: int = 10, 
        document_id: Optional[uuid.UUID] = None,
        similarity_metric: str = "cosine"
    ) -> List[Tuple[Chunk, float]]:
        """
        Perform k-nearest neighbor search on chunks.
        
        Args:
            query_embedding: The query vector
            k: Number of nearest neighbors to return
            document_id: Optional document ID to filter chunks
            similarity_metric: "cosine", "euclidean", or "manhattan"
        
        Returns:
            List of tuples (chunk, similarity_score)
        """
        # Get chunks to search through
        if document_id:
            chunks = self.chunk_repository.get_by_document_id(document_id, limit=10000)  # Get all chunks in document
        else:
            chunks = self.chunk_repository.get_all(limit=10000)  # Get all chunks
        
        if not chunks:
            return []
        
        # Calculate similarity scores
        chunk_scores = []
        for chunk in chunks:
            try:
                if similarity_metric == "cosine":
                    score = self.cosine_similarity(query_embedding, chunk.embedding)
                elif similarity_metric == "euclidean":
                    # Convert distance to similarity (lower distance = higher similarity)
                    distance = self.euclidean_distance(query_embedding, chunk.embedding)
                    score = 1.0 / (1.0 + distance)  # Transform to similarity
                elif similarity_metric == "manhattan":
                    # Convert distance to similarity (lower distance = higher similarity)
                    distance = self.manhattan_distance(query_embedding, chunk.embedding)
                    score = 1.0 / (1.0 + distance)  # Transform to similarity
                else:
                    raise ValueError(f"Unsupported similarity metric: {similarity_metric}")
                
                chunk_scores.append((chunk, score))
            except ValueError:
                # Skip chunks with incompatible embedding dimensions
                continue
        
        # Sort by similarity score (descending) and return top k
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        return chunk_scores[:k]

    def similarity_search_by_library(
        self,
        query_embedding: List[float],
        library_id: uuid.UUID,
        k: int = 10,
        similarity_metric: str = "cosine"
    ) -> List[Tuple[Chunk, float]]:
        """
        Perform similarity search within a specific library.
        This requires getting all documents in the library first.
        """
        from services.document_service import DocumentService
        
        # Get all documents in the library
        document_service = DocumentService(self.chunk_repository.session)
        documents = document_service.get_documents_by_library(library_id)
        
        if not documents:
            return []
        
        # Get all chunks from all documents in the library
        all_chunk_scores = []
        for document in documents:
            chunk_scores = self.knn_search(
                query_embedding=query_embedding,
                k=k * 2,  # Get more candidates from each document
                document_id=document.id,
                similarity_metric=similarity_metric
            )
            all_chunk_scores.extend(chunk_scores)
        
        # Sort all results and return top k
        all_chunk_scores.sort(key=lambda x: x[1], reverse=True)
        return all_chunk_scores[:k]
