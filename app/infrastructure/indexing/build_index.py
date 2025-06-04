import uuid
import logging
from typing import List, Optional, Dict, Any, Union
from sqlmodel import Session

from services.chunk_service import ChunkService
from services.document_service import DocumentService  
from services.library_service import LibraryService
from .linear_index import LinearIndex
from .kd_tree import KDTreeIndex
# Import Chunk model for type hinting in _get_chunks if necessary
from app.core.models import Chunk 


logger = logging.getLogger(__name__)


class IndexBuilder:
    """
    Responsible for building various types of indexes from database data.
    Uses the service layer to read data and populate indexing structures.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.chunk_service = ChunkService(session)
        self.document_service = DocumentService(session)
        self.library_service = LibraryService(session)
    
    def build_index(
        self,
        index_type: str,
        library_id: Optional[uuid.UUID] = None,
        document_id: Optional[uuid.UUID] = None
    ) -> Union[LinearIndex, KDTreeIndex]:
        """Builds a single index of the specified type."""
        logger.info(f"Building {index_type} index for library_id={library_id}, document_id={document_id}")

        if index_type == "linear":
            index: LinearIndex = LinearIndex(vectors=[], ids=[]) 
        elif index_type == "kd_tree":
            index: KDTreeIndex = KDTreeIndex(vectors=[], ids=[]) 
        else:
            logger.error(f"Unsupported index type: {index_type}")
            raise ValueError(f"Unsupported index type: {index_type}")

        all_retrieved_chunks = self._get_chunks(library_id, document_id)

        if not all_retrieved_chunks:
            logger.warning(f"No chunks found to build {index_type} index for scope: library_id={library_id}, document_id={document_id}. Building empty index.")
            index.build() # Build an empty index
            return index

        expected_dim: Optional[int] = None
        for chunk_data in all_retrieved_chunks:
            if chunk_data.embedding and isinstance(chunk_data.embedding, list) and len(chunk_data.embedding) > 0:
                expected_dim = len(chunk_data.embedding)
                break
        
        if expected_dim is None:
            logger.warning(f"No valid embeddings with determinable dimension found for {index_type} index. Scope: library_id={library_id}, document_id={document_id}. Building empty index.")
            index.build()
            return index

        added_count = 0
        for chunk_data in all_retrieved_chunks:
            if chunk_data.embedding and isinstance(chunk_data.embedding, list) and len(chunk_data.embedding) > 0:
                if len(chunk_data.embedding) == expected_dim:
                    index.add_vector(chunk_data.embedding, str(chunk_data.id))
                    added_count += 1
                else:
                    logger.warning(
                        f"Skipping chunk {chunk_data.id} for {index_type} index due to dimension mismatch. "
                        f"Expected {expected_dim}, got {len(chunk_data.embedding)}. Scope: library_id={library_id}, document_id={document_id}"
                    )
            else:
                logger.warning(f"Skipping chunk {chunk_data.id} for {index_type} index due to empty or invalid embedding. Scope: library_id={library_id}, document_id={document_id}")
        
        if added_count == 0:
            logger.warning(f"No valid vectors were added to {index_type} index after filtering. Scope: library_id={library_id}, document_id={document_id}. Building empty index.")
            index.build() 
            return index

        try:
            index.build()
            logger.info(f"Successfully built {index_type} index with {added_count} vectors. Scope: library_id={library_id}, document_id={document_id}")
        except Exception as e:
            logger.error(f"Error building {index_type} index structure: {e}. Scope: library_id={library_id}, document_id={document_id}", exc_info=True)
            raise

        return index
  
    
   
    
    def _get_chunks(
        self,
        library_id: Optional[uuid.UUID] = None,
        document_id: Optional[uuid.UUID] = None
    ) -> List[Chunk]: # Added return type hint
        """
        Internal method to get chunks based on filtering criteria.
        """
        if document_id:
            return self.chunk_service.get_chunks_by_document(document_id, limit=100000) # High limit for indexing
        elif library_id:
            documents = self.document_service.get_documents_by_library(library_id, limit=10000) # High limit
            all_chunks: List[Chunk] = []
            for document in documents:
                doc_chunks = self.chunk_service.get_chunks_by_document(document.id, limit=100000)
                all_chunks.extend(doc_chunks) 
            return all_chunks
        else:
            return self.chunk_service.get_all_chunks(limit=100000) # High limit for global indexing

