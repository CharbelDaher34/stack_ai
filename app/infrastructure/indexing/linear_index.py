import uuid
import numpy as np
from typing import List, Tuple

class LinearIndex:
    def __init__(self,vectors: List[List[float]], ids: List[uuid.UUID]):
        self.vectors: List[np.ndarray] = [np.array(vector) for vector in vectors]
        self.ids: List[uuid.UUID] = ids
        
        print(f"LinearIndex initialized with {len(self.vectors)} vectors and {len(self.ids)} ids")
    
    def add_vector(self, vector: List[float], chunk_id: uuid.UUID) -> None:
        """Adds a vector and its ID to a temporary storage."""
        if not isinstance(vector, list) or not vector:
            # logger.warning(f"Invalid vector provided for chunk_id {chunk_id}. Skipping.")
            return
        if not isinstance(chunk_id, uuid.UUID):
            # logger.warning(f"Invalid chunk_id type for vector {vector}. Skipping.")
            return
        
        self.vectors.append(np.array(vector))
        self.ids.append(chunk_id)
    

    def search(self, query: List[float], k: int) -> List[Tuple[uuid.UUID, float]]:
        """Performs k-NN search. Assumes query vector matches dimension of indexed vectors."""
  
        # Check if we have vectors to search against
        if not self.vectors:
            print(f"No vectors indexed")
            return []
        
        # Convert query to numpy array and validate
        try:
            query_vec = np.array(query)
            if query_vec.size == 0:
                print(f"Empty query vector")
                return []
        except (ValueError, TypeError) as e:
            print(f"Invalid query format: {e}")
            return []
        
        # print(f"Query vector: {query_vec}")
        # print(f"Vectors: {len(self.vectors)}")
        # print(f"Ids: {len(self.ids)}")
        
        # Ensure query_vec dimension matches indexed vectors dimension
        if len(query_vec) != len(self.vectors[0]):
            print(f"Query vector dimension mismatch with indexed vectors. Query: {len(query_vec)}, Indexed: {len(self.vectors[0])}")
            return [] 
            
        distances = [np.linalg.norm(vec - query_vec) for vec in self.vectors]
        # print(f"Distances: {distances}")
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