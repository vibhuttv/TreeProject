import random

class TreapNode:
    def __init__(self, key: int, value: any):
        self.key = key          # The BST key (e.g. partner availability time or ID)
        self.priority = random.random()  # Heap priority
        self.value = value      # The Partner object
        self.left = None
        self.right = None

class Treap:
    """
    Treap (Tree + Heap)
    Maintains items based on BST properties for keys and Heap properties for priorities.
    Used for dynamic reassignment of partners based on specific metrics.
    """
    def __init__(self):
        self.root = None

    def _right_rotate(self, y: TreapNode) -> TreapNode:
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        return x

    def _left_rotate(self, x: TreapNode) -> TreapNode:
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        return y

    def insert(self, key: int, value: any):
        self.root = self._insert_node(self.root, key, value)

    def _insert_node(self, root: TreapNode, key: int, value: any) -> TreapNode:
        if not root:
            return TreapNode(key, value)
            
        if key <= root.key:
            root.left = self._insert_node(root.left, key, value)
            # Fix heap property
            if root.left.priority > root.priority:
                root = self._right_rotate(root)
        else:
            root.right = self._insert_node(root.right, key, value)
            # Fix heap property
            if root.right.priority > root.priority:
                root = self._left_rotate(root)
                
        return root

    def search(self, key: int) -> any:
        node = self._search_node(self.root, key)
        return node.value if node else None

    def _search_node(self, root: TreapNode, key: int) -> TreapNode:
        if root is None or root.key == key:
            return root
        if root.key < key:
            return self._search_node(root.right, key)
        return self._search_node(root.left, key)

    def remove(self, key: int):
        self.root = self._delete_node(self.root, key)

    def _delete_node(self, root: TreapNode, key: int) -> TreapNode:
        if not root:
            return root
            
        if key < root.key:
            root.left = self._delete_node(root.left, key)
        elif key > root.key:
            root.right = self._delete_node(root.right, key)
        # Node to be deleted found
        else:
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
                
            # Both children exist
            if root.left.priority < root.right.priority:
                root = self._left_rotate(root)
                root.left = self._delete_node(root.left, key)
            else:
                root = self._right_rotate(root)
                root.right = self._delete_node(root.right, key)
                
        return root

    def get_all_values(self):
        values = []
        def _inorder(node):
            if node:
                _inorder(node.left)
                values.append(node.value)
                _inorder(node.right)
        _inorder(self.root)
        return values
