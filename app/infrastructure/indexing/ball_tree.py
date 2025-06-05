import numpy as np
from typing import List, Optional, Tuple

class BallTreeNode:
    def __init__(self, points: List[np.ndarray], ids: List[str]):
        self.points = points
        self.ids = ids
        self.left: Optional[BallTreeNode] = None
        self.right: Optional[BallTreeNode] = None
        self.centroid = np.mean(points, axis=0) if len(points) > 0 else None
        self.radius = max(np.linalg.norm(p - self.centroid) for p in points) if points else 0

class BallTree:
    def __init__(self, vectors: List[List[float]], ids: List[str], leaf_size: int = 1):
        self.leaf_size = leaf_size
        self.vectors: List[np.ndarray] = [np.array(vector) for vector in vectors]
        self.ids: List[str] = ids
        print(f"BallTree initialized with {len(self.vectors)} vectors and {len(self.ids)} ids")
        self.root = self._build(self.vectors, self.ids)

    def _build(self, points: List[np.ndarray], ids: List[str]) -> Optional[BallTreeNode]:
        if not points:
            return None

        node = BallTreeNode(points, ids)
        if len(points) <= self.leaf_size:
            return node

        # Find two farthest points using a more reliable method
        max_distance = -1
        p1, p2 = points[0], points[0]
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dist = np.linalg.norm(points[i] - points[j])
                if dist > max_distance:
                    max_distance = dist
                    p1, p2 = points[i], points[j]

        # Partition points based on distance to p1 or p2
        left_points = []
        left_ids = []
        right_points = []
        right_ids = []
        for i, p in enumerate(points):
            if np.linalg.norm(p - p1) < np.linalg.norm(p - p2):
                left_points.append(p)
                left_ids.append(ids[i])
            else:
                right_points.append(p)
                right_ids.append(ids[i])

        # Handle edge case where partition might be empty
        if not left_points:
            mid = len(right_points) // 2
            left_points = right_points[:mid]
            left_ids = right_ids[:mid]
            right_points = right_points[mid:]
            right_ids = right_ids[mid:]
        elif not right_points:
            mid = len(left_points) // 2
            right_points = left_points[:mid]
            right_ids = left_ids[:mid]
            left_points = left_points[mid:]
            left_ids = left_ids[mid:]

        node.left = self._build(left_points, left_ids)
        node.right = self._build(right_points, right_ids)
        return node

    def _search(self, node: BallTreeNode, query: np.ndarray, best: tuple) -> tuple:
        if node is None or node.centroid is None:
            return best

        dist_to_centroid = np.linalg.norm(query - node.centroid)
        if dist_to_centroid - node.radius > best[0]:
            return best  # prune this subtree

        # If leaf node, check all points
        if node.left is None and node.right is None:
            for i, p in enumerate(node.points):
                d = np.linalg.norm(query - p)
                if d < best[0]:
                    best = (d, p, node.ids[i])
            return best

        # Determine closer child
        left_dist = np.linalg.norm(query - node.left.centroid) if node.left else float('inf')
        right_dist = np.linalg.norm(query - node.right.centroid) if node.right else float('inf')

        closer = node.left if left_dist < right_dist else node.right
        further = node.right if closer is node.left else node.left

        best = self._search(closer, query, best)
        # Only search further child if potentially useful
        if further and (right_dist if closer is node.left else left_dist) - (further.radius if further else 0) < best[0]:
            best = self._search(further, query, best)
        return best

    def add_vector(self, vector: List[float], chunk_id: str) -> None:
        """Adds a vector and its ID to the index."""
        if not isinstance(vector, list) or not vector:
            return
        if not isinstance(chunk_id, str):
            return
        
        self.vectors.append(np.array(vector))
        self.ids.append(chunk_id)
        # Rebuild entire tree
        self.root = self._build(self.vectors, self.ids)

    def search(self, query: List[float], k: int) -> List[Tuple[str, float]]:
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
        
        if self.root is None:
            return []
        
        # For k-NN search, we need to find k nearest neighbors
        # We'll use a simple approach: find all distances and sort
        all_results = []
        for i, vec in enumerate(self.vectors):
            distance = np.linalg.norm(vec - query_vec)
            all_results.append((self.ids[i], distance))
        
        # Sort by distance and return top k
        all_results.sort(key=lambda x: x[1])
        actual_k = min(k, len(all_results))
        return all_results[:actual_k]

# Example usage (keeping for compatibility)
if __name__ == "__main__":
    # Generate sample 2D points
    data = [[np.random.rand(), np.random.rand()] for _ in range(100)]
    ids = [f"point_{i}" for i in range(100)]

    # Build the tree
    tree = BallTree(data, ids)

    # Query a point
    query_point = [0.5, 0.5]
    nearest = tree.search(query_point, k=1)

    print("Query:", query_point)
    print("Nearest:", nearest)

    tree.add_vector([0.501, 0.5001], "new_point")

    nearest = tree.search(query_point, k=1)

    print("Query:", query_point)
    print("Nearest:", nearest)