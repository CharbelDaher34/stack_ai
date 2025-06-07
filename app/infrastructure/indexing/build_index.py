import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.models import ChunkCreateRequest

import uuid
import logging
from typing import List, Optional, Dict, Any, Union, Tuple
from core.db import get_session
from sqlmodel import Session
import time
import threading
from services.chunk_service import ChunkService
from services.document_service import DocumentService  
from services.library_service import LibraryService

# Import Chunk model for type hinting in _get_chunks if necessary
from core.models import Chunk, ChunkRead
from sentence_transformers import SentenceTransformer
import os
import numpy as np
logger = logging.getLogger(__name__)
try:
    from .linear_index import LinearIndex
    from .kd_tree import KDTreeIndex
    from .ball_tree import BallTree
except:
    from infrastructure.indexing.ball_tree import BallTree
    from infrastructure.indexing.kd_tree import KDTreeIndex
    from infrastructure.indexing.linear_index import LinearIndex

class IndexBuilder:
    """
    Responsible for building various types of indexes from database data.
    Uses the service layer to read data and populate indexing structures.
    """
    
    def __init__(self, session: Session,index_types: List[str]):
        self.session = session
        self.chunk_service = ChunkService(session)
        self.document_service = DocumentService(session)
        self.library_service = LibraryService(session)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index: Dict[str, Union[LinearIndex, BallTree, KDTreeIndex]] = {}
        self._lock = threading.Lock()
        for index_type in index_types:
            self.build_index(index_type)
    def build_index(
        self,
        index_type: str,
        library_id: Optional[uuid.UUID] = None,
        document_id: Optional[uuid.UUID] = None
    ) -> Tuple[Union[LinearIndex, BallTree, KDTreeIndex], float]:
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
            return self.index[index_type]
        else:
            start_time = time.time()
            if index_type == "linear":
                start_time = time.time()
                self.index[index_type] = LinearIndex(vectors=vectors, ids=ids) 
            elif index_type == "kd_tree": 
                self.index[index_type] = KDTreeIndex(vectors=vectors, ids=ids)
            elif index_type == "ball_tree":
                self.index[index_type] = BallTree(vectors=vectors, ids=ids) 
            else:
                logger.error(f"Unsupported index type: {index_type}")
                raise ValueError(f"Unsupported index type: {index_type}")
            end_time = time.time()
    

        print(f"Build time for {index_type}: {end_time - start_time} seconds")
        return self.index[index_type]
    def add_vector(self, vector: List[float], id: uuid.UUID):
        """Adds a vector to the index."""
        # Ensure vector is a list for compatibility
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()
        with self._lock:
            for index_type in self.index.keys():
                print(f"Adding vector to {index_type} index")
                self.index[index_type].add_vector(vector, id)
              
    def add_vector_by_text(self, text: str,random_chunk: bool = False):
        """Adds a vector to the index."""
        if random_chunk:
            chunk=self.chunk_service.create_chunk(ChunkCreateRequest(text=text,document_id=str(uuid.uuid4())),random_chunk=True)
       
        vector = self.model.encode(text)
        self.add_vector(vector, chunk.id)
    
    def search_index(self, query: str, k: int,index_type: str) -> List[ChunkRead|dict]:
        """Searches the index for the nearest neighbors to the query vector."""
        query_embedding = self.model.encode(query)
        with self._lock:
            start_time = time.time()
            result = self.index[index_type].search(query_embedding, k)
            end_time = time.time()
        
        list_of_chunks=[]
        for chunk_id, distance in result:
            chunk = self.chunk_service.get_chunk(chunk_id)
            if chunk:   
                list_of_chunks.append(chunk)
            else:
                list_of_chunks.append({"id":chunk_id,"distance":distance})
        print(f"Search time for {index_type}: {end_time - start_time} seconds")
        return list_of_chunks#, end_time - start_time
   
    
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

if __name__ == "__main__":
    print("Starting index builder")
    session = next(get_session())
    index_builder = IndexBuilder(session, index_types=["ball_tree", "linear"])
    
    # Print initial state
    print("\nInitial state:")
    print(f"Ball tree vectors: {len(index_builder.index['ball_tree'].vectors)}")
    print(f"Linear index vectors: {len(index_builder.index['linear'].vectors)}")
    
    # Test text to add
    test_text = "i am charbel daher and i am a bad person"
    print(f"\nAdding test text: {test_text}")
    
 
  
    index_builder.add_vector_by_text(test_text)
    
    # Print state after adding
    print("\nState after adding vector:")
    print(f"Ball tree vectors: {len(index_builder.index['ball_tree'].vectors)}")
    print(f"Ball tree IDs: {len(index_builder.index['ball_tree'].ids)}")
    print(f"Linear index vectors: {len(index_builder.index['linear'].vectors)}")
    print(f"Linear index IDs: {len(index_builder.index['linear'].ids)}")
    
  
    # Verify vector was added by searching immediately
    print("\nSearching with ball_tree index...")
    ball_tree_results = index_builder.search_index(test_text, 1, "ball_tree")  # Increased k to see more results
    print(f"Ball tree results: {[chunk.text for chunk in ball_tree_results]}")
    
    print("\nSearching with linear index...")
    linear_results = index_builder.search_index(test_text, 1, "linear")  # Increased k to see more results
    print(f"Linear results: {[chunk.text for chunk in linear_results]}")
    
    # Try a different search query to see if it finds our text
    different_query = "bad"
    print(f"\nSearching with different query: {different_query}")
    ball_tree_results = index_builder.search_index(different_query, 1, "ball_tree")
    print(f"Ball tree results: {[chunk.text for chunk in ball_tree_results]}")
    
    linear_results = index_builder.search_index(different_query, 1, "linear")
    print(f"Linear results: {[chunk.text for chunk in linear_results]}")
