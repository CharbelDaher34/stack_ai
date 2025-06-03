import numpy as np
from typing import List, Tuple

class LinearIndex:
    def __init__(self):
        self.vectors = []
        self.ids = []
    
    def add_vector(self, vector: List[float], chunk_id: str) -> None:
        self.vectors.append(np.array(vector))
        self.ids.append(chunk_id)
    
    def knn_search(self, query: List[float], k: int) -> List[Tuple[str, float]]:
        query_vec = np.array(query)
        distances = [np.linalg.norm(vec - query_vec) for vec in self.vectors]
        sorted_indices = np.argsort(distances)[:k]
        return [(self.ids[i], distances[i]) for i in sorted_indices]
    
    # Space: O(n*d), Time: O(n) per query
    # Chosen for simplicity and exact results