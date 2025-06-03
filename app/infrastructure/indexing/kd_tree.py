import numpy as np
from typing import List, Tuple

class KDNode:
    def __init__(self, vector, chunk_id, left=None, right=None):
        self.vector = vector
        self.chunk_id = chunk_id
        self.left = left
        self.right = right

class KDTreeIndex:
    def __init__(self):
        self.root = None
    
    def build(self, vectors, ids, depth=0):
        if not vectors:
            return None
        
        k = len(vectors[0])
        axis = depth % k
        
        sorted_indices = np.argsort([v[axis] for v in vectors])
        mid = len(sorted_indices) // 2
        
        node = KDNode(
            vectors[sorted_indices[mid]],
            ids[sorted_indices[mid]],
            self.build([vectors[i] for i in sorted_indices[:mid]], 
                      [ids[i] for i in sorted_indices[:mid]], depth+1),
            self.build([vectors[i] for i in sorted_indices[mid+1:]], 
                      [ids[i] for i in sorted_indices[mid+1:]], depth+1)
        )
        return node
    
    # Space: O(n*d), Time: O(log n) average case
    # Chosen for efficient nearest neighbor in low dimensions