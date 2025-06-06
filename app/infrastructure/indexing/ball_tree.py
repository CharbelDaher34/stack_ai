import uuid
import numpy as np
from typing import List, Optional, Tuple
import heapq

class BallTreeNode:
    def __init__(self, points: List[np.ndarray], ids: List[uuid.UUID]):
        self.points = points
        self.ids = ids
        self.left: Optional[BallTreeNode] = None
        self.right: Optional[BallTreeNode] = None
        self.centroid = np.mean(points, axis=0) if len(points) > 0 else None
        self.radius = max(np.linalg.norm(p - self.centroid) for p in points) if points else 0

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

class BallTree:
    def __init__(self, vectors: List[List[float]], ids: List[uuid.UUID], leaf_size: int = 20):
        self.leaf_size = leaf_size
        self.vectors: List[np.ndarray] = [np.array(vector) for vector in vectors]
        self.ids: List[uuid.UUID] = ids
        print(f"BallTree initialized with {len(self.vectors)} vectors and {len(self.ids)} ids")
        self.root = self._build(self.vectors, self.ids)

    def _build(self, points: List[np.ndarray], ids: List[uuid.UUID]) -> Optional[BallTreeNode]:
        if not points:
            return None

        node = BallTreeNode(points, ids)
        if len(points) <= self.leaf_size:
            return node
        
        # Split the node and create children recursively
        self._split_node(node)
        
        node.left = self._build(node.left.points, node.left.ids)
        node.right = self._build(node.right.points, node.right.ids)
        
        # An internal node doesn't need to store points after splitting
        node.points = []
        node.ids = []
        
        return node

    def _split_node(self, node: BallTreeNode):
        """Splits a node into two children, left and right."""
        # Find two farthest points to define the split
        max_distance = -1
        p1_idx, p2_idx = 0, 0
        for i in range(len(node.points)):
            for j in range(i + 1, len(node.points)):
                dist = np.linalg.norm(node.points[i] - node.points[j])
                if dist > max_distance:
                    max_distance = dist
                    p1_idx, p2_idx = i, j
        
        p1, p2 = node.points[p1_idx], node.points[p2_idx]

        # Partition points based on distance to p1 or p2
        left_points, left_ids, right_points, right_ids = [], [], [], []
        for i, p in enumerate(node.points):
            if np.linalg.norm(p - p1) < np.linalg.norm(p - p2):
                left_points.append(p)
                left_ids.append(node.ids[i])
            else:
                right_points.append(p)
                right_ids.append(node.ids[i])

        # Handle edge cases where one partition is empty
        if not left_points or not right_points:
            mid = len(node.points) // 2
            left_points, left_ids = node.points[:mid], node.ids[:mid]
            right_points, right_ids = node.points[mid:], node.ids[mid:]
        
        node.left = BallTreeNode(left_points, left_ids)
        node.right = BallTreeNode(right_points, right_ids)

    def add_vector(self, vector: List[float], chunk_id: uuid.UUID):
        """Adds a vector and its ID to the index without rebuilding."""
        if not isinstance(vector, list) or not vector or not isinstance(chunk_id, uuid.UUID):
            return

        point = np.array(vector)
        
        # Always add to main storage first (for tracking and validation)
        self.vectors.append(point)
        self.ids.append(chunk_id)
        
        if self.root is None:
            # If tree is empty, build the root
            self.root = self._build([point], [chunk_id])
        else:
            # If tree exists, insert into tree structure
            self._insert(self.root, point, chunk_id)

    def _insert(self, node: BallTreeNode, point: np.ndarray, id: uuid.UUID):
        """Recursively finds the best leaf to insert the point."""
        
        # If it's a leaf, add the point
        if node.is_leaf():
            node.points.append(point)
            node.ids.append(id)
            
            # If the leaf is now too big, split it
            if len(node.points) > self.leaf_size:
                self._split_node(node)
                # The original points are now in children, clear from this node
                node.points = []
                node.ids = []
        else:
            # Not a leaf, decide which child to traverse
            dist_to_left = np.linalg.norm(point - node.left.centroid)
            dist_to_right = np.linalg.norm(point - node.right.centroid)
            if dist_to_left < dist_to_right:
                self._insert(node.left, point, id)
            else:
                self._insert(node.right, point, id)
        
        # Update centroid and radius on the way back up
        self._update_node_bounds(node)
     
    def _update_node_bounds(self, node: BallTreeNode):
        """Updates the centroid and radius of a node based on its children."""
        if node.is_leaf():
            # For leaf nodes, recalculate centroid and radius from points
            if len(node.points) > 0:
                node.centroid = np.mean(node.points, axis=0)
                node.radius = max(np.linalg.norm(p - node.centroid) for p in node.points)
        else:
            # For internal nodes, update based on child centroids and radii
            if node.left and node.right:
                # Update centroid as the average of child centroids
                node.centroid = (node.left.centroid + node.right.centroid) / 2
                
                # Radius must enclose both child balls
                rad_left = np.linalg.norm(node.left.centroid - node.centroid) + node.left.radius
                rad_right = np.linalg.norm(node.right.centroid - node.centroid) + node.right.radius
                node.radius = max(rad_left, rad_right)

    def _search_k(self, node: BallTreeNode, query: np.ndarray, k: int, heap: List[Tuple[float, uuid.UUID]]):
        """Recursive k-NN search using a heap for pruning."""
        if node is None:
            return

        # Pruning check: if the farthest point in our heap is closer than
        # the nearest possible point in this ball, prune the branch.
        if len(heap) == k:
            farthest_dist = -heap[0][0] # Heap stores negative distances
            dist_to_centroid = np.linalg.norm(query - node.centroid)
            if dist_to_centroid - node.radius > farthest_dist:
                return

        # If it's a leaf, compare with all points in it
        if node.is_leaf():
            for i, p in enumerate(node.points):
                d = np.linalg.norm(query - p)
                if len(heap) < k:
                    heapq.heappush(heap, (-d, str(node.ids[i])))
                else:
                    # heappushpop is more efficient than a separate push and pop
                    heapq.heappushpop(heap, (-d, str(node.ids[i])))
            return

        # It's an internal node, decide which child to visit first
        dist_left = np.linalg.norm(query - node.left.centroid)
        dist_right = np.linalg.norm(query - node.right.centroid)

        # Visit the closer child first to improve pruning effectiveness
        if dist_left < dist_right:
            self._search_k(node.left, query, k, heap)
            self._search_k(node.right, query, k, heap)
        else:
            self._search_k(node.right, query, k, heap)
            self._search_k(node.left, query, k, heap)

    def search(self, query: List[float], k: int) -> List[Tuple[uuid.UUID, float]]:
        """Performs k-NN search using the Ball Tree for pruning."""
        if not self.vectors or self.root is None:
            print("No vectors indexed")
            return []

        try:
            query_vec = np.array(query, dtype=np.float32)
            if query_vec.shape[0] != self.root.centroid.shape[0]:
                print(f"Query vector dimension mismatch.")
                return []
        except (ValueError, TypeError) as e:
            print(f"Invalid query format: {e}")
            return []

        # Use a max-heap to find the k nearest neighbors
        # We store (-distance, id) to simulate a max-heap with a min-heap.
        results_heap: List[Tuple[float, uuid.UUID]] = []
        self._search_k(self.root, query_vec, k, results_heap)

        # Dequeue, sort, and format the results
        # The heap is not sorted, so we must sort the final list
        final_results = [(id,distance) for distance, id in results_heap]
        final_results.sort(key=lambda x: x[1])
        
        return final_results
# Example usage (keeping for compatibility)
if __name__ == "__main__":
    # Generate sample 2D points
    data = [[np.random.rand(), np.random.rand()] for _ in range(100)]
    ids = [uuid.uuid4() for _ in range(100)]

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