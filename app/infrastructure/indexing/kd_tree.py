import numpy as np
import math
from typing import List, Tuple
import heapq

class KDNode:
    def __init__(self, vector, chunk_id, left=None, right=None):
        self.vector = np.array(vector) # Store as numpy array for consistency
        self.chunk_id = chunk_id
        self.left = left
        self.right = right

class KDTreeIndex:
    def __init__(self,vectors: List[List[float]], ids: List[str]):
        self.root: KDNode | None = None
        self.vectors: List[Tuple[List[float],str]] = [(vector, id) for vector, id in zip(vectors, ids)]

    
    def add_vector(self, vector: List[float], chunk_id: str) -> None:
        """Adds a vector and its ID to a temporary storage."""
        if not isinstance(vector, list) or not vector:
            # logger.warning(f"Invalid vector provided for chunk_id {chunk_id}. Skipping.")
            return
        if not isinstance(chunk_id, str):
            # logger.warning(f"Invalid chunk_id type for vector {vector}. Skipping.")
            return
        
        # Basic dimension check during add_vector for early feedback
        if not self.vectors and vector: # First vector sets the dimension
             pass # Dimension will be set during build based on filtered data
        elif self.vectors and vector :
            # logger.warning(f"Vector for chunk_id {chunk_id} has mismatched dimension. Expected {self.dimension}, got {len(vector)}. Skipping.")
            # This specific vector will be skipped by build anyway if IndexBuilder doesn't filter it.
            pass # Let build handle final filtering for consistency

        self.vectors.append((vector, chunk_id))

    def build(self) -> None:
        """Processes temporarily stored data and builds the KD-Tree."""
        if not self.vectors:
            self.root = None
            self.dimension = None
            return

        valid_vectors = []
        valid_ids = []
        current_dimension = None

        # Determine dimension from the first valid vector and filter
        for vec_list, id_str in self.vectors:
            if vec_list and isinstance(vec_list, list):
                if current_dimension is None:
                    current_dimension = len(vec_list)
                
                if len(vec_list) == current_dimension:
                    valid_vectors.append(vec_list) # Keep as list of lists for np.argsort
                    valid_ids.append(id_str)
                # else:
                    # logger.warning(f"Skipping vector for chunk_id {id_str} due to dimension mismatch in KDTreeIndex.build. Expected {current_dimension}.")
        
        if not valid_vectors:
            self.root = None
        else:
            self.root = self._build_recursive(valid_vectors, valid_ids)
        
        self._temp_data = [] # Clear temporary storage

    def _build_recursive(self, vectors: List[List[float]], ids: List[str], depth: int = 0) -> KDNode | None:
        """Recursive helper to build the KD-Tree."""
        if not vectors:
            return None
        
        k = len(vectors[0])
        axis = depth % k
        
        # Sort points by the current axis and choose median
        # Need to handle np.array conversion if vectors are still lists of floats
        # For np.argsort, it's better if it's a list of lists/tuples, then access element by [axis]
        try:
            sorted_indices = sorted(range(len(vectors)), key=lambda i: vectors[i][axis])
        except IndexError:
            # This can happen if a vector doesn't have the expected dimension.
            # Should be caught by the filtering in build() or earlier in IndexBuilder.
            # logger.error(f"IndexError during KD-Tree build at axis {axis}. Check vector dimensions.")
            # Attempt to filter out malformed vectors here as a last resort
            consistent_vectors = []
            consistent_ids = []
            for idx, v in enumerate(vectors):
                if len(v) == k:
                    consistent_vectors.append(v)
                    consistent_ids.append(ids[idx])
            if not consistent_vectors or len(vectors) == len(consistent_vectors): # no change or all bad
                 return None # Cannot proceed if malformed data persists
            vectors, ids = consistent_vectors, consistent_ids
            sorted_indices = sorted(range(len(vectors)), key=lambda i: vectors[i][axis])
            
        mid_idx = len(sorted_indices) // 2
        median_original_idx = sorted_indices[mid_idx]
        
        # Create node and construct subtrees
        node = KDNode(
            vectors[median_original_idx],
            ids[median_original_idx]
        )
        
        # Correctly partition data for left and right children
        left_indices = sorted_indices[:mid_idx]
        right_indices = sorted_indices[mid_idx+1:]
        
        node.left = self._build_recursive(
            [vectors[i] for i in left_indices],
            [ids[i] for i in left_indices],
            depth + 1
        )
        node.right = self._build_recursive(
            [vectors[i] for i in right_indices],
            [ids[i] for i in right_indices],
            depth + 1
        )
        
        return node
    
    def search(self, query: List[float], k: int) -> List[Tuple[str, float]]:
        """Perform k-nearest neighbor search using the KD-tree."""
        if self.root is None or not query:
            return []
        
        if len(query) != len(self.vectors[0]):
            # logger.error(f"Query dimension {len(query)} mismatch with tree dimension {self.dimension}.")
            return []

        query_vec = np.array(query)
        best: List[Tuple[float, str]] = [] # Stores (-distance, chunk_id) for max-heap behavior
        
        def distance_sq(v1_np: np.ndarray, v2_list: List[float]) -> float: # Changed v2 to list for initial query
            # Assumes v1_np is already np.array (node.vector)
            v2_np = np.array(v2_list) # Convert query or other vectors as needed
            return np.sum((v1_np - v2_np)**2)
        
        def search_kd_tree_recursive(node: KDNode | None, depth: int = 0):
            if node is None:
                return
            
            dist_sq_val = distance_sq(node.vector, query) # node.vector is already np.array
            
            if len(best) < k:
                heapq.heappush(best, (-dist_sq_val, node.chunk_id))
            elif dist_sq_val < -best[0][0]:
                heapq.heapreplace(best, (-dist_sq_val, node.chunk_id))
            
            axis = depth % len(self.vectors[0])
            diff_axis = query_vec[axis] - node.vector[axis]
            
            # Choose which subtree to explore first
            closer_child = node.left if diff_axis < 0 else node.right
            farther_child = node.right if diff_axis < 0 else node.left
            
            search_kd_tree_recursive(closer_child, depth + 1)
            
            # Check if we need to search the farther branch
            # Pruning condition: if the hypersphere defined by current k-th best distance
            # intersects the splitting hyperplane of the current node.
            # The distance to hyperplane is abs(query[axis] - node.point[axis])
            # We compare squared distances to avoid sqrt
            if len(best) < k or (diff_axis**2) < -best[0][0]:
                search_kd_tree_recursive(farther_child, depth + 1)
        
        search_kd_tree_recursive(self.root)
        
        # Convert heap to sorted list (closest first), distances are actual distances
        result = [ (chunk_id, math.sqrt(-neg_dist_sq)) for neg_dist_sq, chunk_id in sorted(best, reverse=True) ]
        return result
    
    # Space: O(n*d), Time: O(log n) average case for search after build
    # Chosen for efficient nearest neighbor in low dimensions