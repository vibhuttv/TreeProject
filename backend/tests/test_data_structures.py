import unittest
from data_structures.kd_tree import KDTree
from data_structures.priority_queue import PriorityQueue
from data_structures.treap import Treap
import uuid

class DummyItem:
    def __init__(self, id_):
        self.id = id_

class TestDataStructures(unittest.TestCase):
    def test_priority_queue(self):
        pq = PriorityQueue()
        self.assertTrue(pq.is_empty())
        
        pq.push(1, DummyItem("low"))
        pq.push(10, DummyItem("high"))
        pq.push(5, DummyItem("med"))
        
        self.assertFalse(pq.is_empty())
        
        item = pq.pop()
        self.assertEqual(item.id, "high")
        item = pq.pop()
        self.assertEqual(item.id, "med")
        
    def test_kd_tree(self):
        tree = KDTree()
        item1 = DummyItem("1")
        item2 = DummyItem("2")
        item3 = DummyItem("3")
        
        tree.insert((10, 10), item1)
        tree.insert((50, 50), item2)
        tree.insert((20, 20), item3)
        
        nearest = tree.nearest_neighbor((12, 12))
        self.assertEqual(nearest.id, "1")
        
        nearest2 = tree.nearest_neighbor((45, 45))
        self.assertEqual(nearest2.id, "2")
        
        in_range = tree.range_search((15, 15), 10)
        # Should find (10,10) and (20,20) because sqrt(50) = 7.07 < 10
        self.assertEqual(len(in_range), 2)
        
    def test_treap(self):
        treap = Treap()
        item1 = DummyItem("P1")
        item2 = DummyItem("P2")
        
        treap.insert(100, item1)
        treap.insert(50, item2)
        
        res = treap.search(50)
        self.assertIsNotNone(res)
        self.assertEqual(res.id, "P2")
        
        treap.remove(50)
        self.assertIsNone(treap.search(50))

if __name__ == '__main__':
    unittest.main()
