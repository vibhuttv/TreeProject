import math
from typing import List, Tuple, Optional

class Node:
    def __init__(self, location: Tuple[float, float], data: any):
        self.location = location
        self.data = data
        self.left = None
        self.right = None

class KDTree:
    def __init__(self):
        self.root = None

    def insert(self, location: Tuple[float, float], data: any):
        def _insert(node, depth):
            if not node:
                return Node(location, data)
            
            k = 2  # 2D KD-Tree
            axis = depth % k
            
            if location[axis] < node.location[axis]:
                node.left = _insert(node.left, depth + 1)
            else:
                # We could have items with the exact same coordinate, just put them to right
                node.right = _insert(node.right, depth + 1)
            return node
            
        self.root = _insert(self.root, 0)

    def nearest_neighbor(self, target: Tuple[float, float]) -> Optional[any]:
        best_node = None
        best_dist = float('inf')
        
        def _search(node, depth):
            nonlocal best_node, best_dist
            if not node:
                return
            
            k = 2
            axis = depth % k
            
            # Distance from target to current node
            d = math.hypot(node.location[0] - target[0], node.location[1] - target[1])
            if d < best_dist:
                best_dist = d
                best_node = node.data
                
            # Which child to search first
            if target[axis] < node.location[axis]:
                first, second = node.left, node.right
            else:
                first, second = node.right, node.left
                
            _search(first, depth + 1)
            
            # Check if we need to explore the other branch
            if abs(target[axis] - node.location[axis]) < best_dist:
                _search(second, depth + 1)

        _search(self.root, 0)
        return best_node

    def range_search(self, target: Tuple[float, float], radius: float) -> List[any]:
        results = []
        
        def _search(node, depth):
            if not node:
                return
                
            k = 2
            axis = depth % k
            
            # Distance from target to current node
            d = math.hypot(node.location[0] - target[0], node.location[1] - target[1])
            if d <= radius:
                results.append(node.data)
                
            if target[axis] - radius < node.location[axis]:
                _search(node.left, depth + 1)
            if target[axis] + radius >= node.location[axis]:
                _search(node.right, depth + 1)
                
        _search(self.root, 0)
        return results

    def remove(self, data_id: str):
        # A simple approach for removal is to rebuild the tree without the removed node,
        # or implement proper KD tree removal.
        # Since rebuilding might be O(N) but partners count might be manageable, 
        # let's collect all and rebuild
        nodes = self._get_all(self.root)
        self.root = None
        for n in nodes:
            if n.data.id != data_id:  # assuming data has an 'id' attribute
                self.insert(n.location, n.data)

    def _get_all(self, node) -> List[Node]:
        if not node:
            return []
        return [node] + self._get_all(node.left) + self._get_all(node.right)
