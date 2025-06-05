import uuid
import logging
from typing import List, Optional, Dict, Any, Union, Tuple
from sqlmodel import Session
import time
from services.chunk_service import ChunkService
from services.document_service import DocumentService  
from services.library_service import LibraryService
from .linear_index import LinearIndex
from .kd_tree import KDTreeIndex
from .ball_tree import BallTree
# Import Chunk model for type hinting in _get_chunks if necessary
from core.models import Chunk 
from sentence_transformers import SentenceTransformer

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
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index: Union[LinearIndex, KDTreeIndex, BallTree] = None
    def build_index(
        self,
        index_type: str,
        library_id: Optional[uuid.UUID] = None,
        document_id: Optional[uuid.UUID] = None
    ) -> Union[LinearIndex, KDTreeIndex]:
        """Builds a single index of the specified type."""
        logger.info(f"Building {index_type} index for library_id={library_id}, document_id={document_id}")

      
        all_retrieved_chunks = self._get_chunks(library_id, document_id)
        ids=[]
        vectors=[]
        for chunk in all_retrieved_chunks:
            ids.append(str(chunk.id))
            vectors.append(chunk.embedding)
        if not all_retrieved_chunks:
            logger.warning(f"No chunks found to build {index_type} index for scope: library_id={library_id}, document_id={document_id}. Building empty index.")
            return self.index
        else:
            start_time = time.time()
            if index_type == "linear":
                start_time = time.time()
                self.index: LinearIndex = LinearIndex(vectors=vectors, ids=ids) 
            elif index_type == "kd_tree":
                self.index: KDTreeIndex = KDTreeIndex(vectors=vectors, ids=ids) 
            elif index_type == "ball_tree":
                self.index: BallTree = BallTree(vectors=vectors, ids=ids) 
            else:
                logger.error(f"Unsupported index type: {index_type}")
                raise ValueError(f"Unsupported index type: {index_type}")
            end_time = time.time()
            print(f"Time taken to build {index_type} index: {end_time - start_time} seconds")
        # added_count = 0
        # for chunk_data in all_retrieved_chunks:
        #     if chunk_data.embedding and isinstance(chunk_data.embedding, list) and len(chunk_data.embedding) > 0:
        #         self.index.add_vector(chunk_data.embedding, str(chunk_data.id))
        #         added_count += 1
               
        #     else:
        #         logger.warning(f"Skipping chunk {chunk_data.id} for {index_type} index due to empty or invalid embedding. Scope: library_id={library_id}, document_id={document_id}")
        
        # if added_count == 0:
        #     logger.warning(f"No valid vectors were added to {index_type} index after filtering. Scope: library_id={library_id}, document_id={document_id}. Building empty index.")
        #     return self.index
        # print(f"Added {added_count} vectors to {index_type} index")
        print(f"Vectors: {len(self.index.vectors)}")
        print(f"Ids: {len(self.index.ids)}")
        return self.index
  
    def search_index(self, query: str, k: int) -> List[Tuple[str, float]]:
        """Searches the index for the nearest neighbors to the query vector."""
        query_embedding = self.model.encode(query)
        start_time = time.time()
        result = self.index.search(query_embedding, k)
        end_time = time.time()
        print(f"Time taken to search {self.index.__class__.__name__} index: {end_time - start_time} seconds")
        return result
   
    
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
                doc_chunks = self.chunk_service.get_chunks_by_document(document.id, limit=100000, for_indexing=True)
                all_chunks.extend(doc_chunks) 
            return all_chunks
        else:
            return self.chunk_service.get_all_chunks(limit=100000, for_indexing=True) # High limit for global indexing

