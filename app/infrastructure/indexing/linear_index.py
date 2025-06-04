import numpy as np
from typing import List, Tuple

class LinearIndex:
    def __init__(self,vectors: List[List[float]], ids: List[str]):
        self.vectors: List[np.ndarray] = [np.array(vector) for vector in vectors]
        self.ids: List[str] = ids
    
    def add_vector(self, vector: List[float], chunk_id: str) -> None:
        """Adds a vector and its ID to a temporary storage."""
        if not isinstance(vector, list) or not vector:
            # logger.warning(f"Invalid vector provided for chunk_id {chunk_id}. Skipping.")
            return
        if not isinstance(chunk_id, str):
            # logger.warning(f"Invalid chunk_id type for vector {vector}. Skipping.")
            return
        
        self.vectors.append(np.array(vector))
        self.ids.append(chunk_id)
    

    def search(self, query: List[float], k: int) -> List[Tuple[str, float]]:
        """Performs k-NN search. Assumes query vector matches dimension of indexed vectors."""
        if not self.vectors or not query:
            return []
        
        query_vec = np.array(query)
        
        # Ensure query_vec dimension matches indexed vectors dimension if vectors exist
        if self.vectors and len(query_vec) != len(self.vectors[0]):
            # logger.error("Query vector dimension mismatch with indexed vectors.")
            # Or raise ValueError
            return [] 
            
        distances = [np.linalg.norm(vec - query_vec) for vec in self.vectors]
        
        if not distances:
            return []
            
        # Get indices of k smallest distances
        # Using np.argsort and then selecting top k
        # If k is larger than number of items, return all items sorted
        num_items = len(distances)
        actual_k = min(k, num_items)
        
        sorted_indices = np.argsort(distances)[:actual_k]
        return [(self.ids[i], distances[i]) for i in sorted_indices]
    
    # Space: O(n*d), Time: O(n*d) per query after build
    # Chosen for simplicity and exact results