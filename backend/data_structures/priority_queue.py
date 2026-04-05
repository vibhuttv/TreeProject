from typing import Any, Tuple

class PriorityQueue:
    def __init__(self):
        # Array representation of heap
        # Elements are tuple (priority, item)
        # We want a max-heap if higher number = higher priority
        self.heap = []

    def push(self, priority: int, item: Any):
        # We store -priority internally to use as a max heap using standard comparisons
        # Or just write custom bubble up/down
        self.heap.append((priority, item))
        self._bubble_up(len(self.heap) - 1)

    def pop(self) -> Any:
        if not self.heap:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()[1]
            
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._bubble_down(0)
        return root[1]

    def peek(self) -> Any:
        if self.heap:
            return self.heap[0][1]
        return None

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def _bubble_up(self, index: int):
        parent = (index - 1) // 2
        
        if index > 0 and self.heap[index][0] > self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._bubble_up(parent)

    def _bubble_down(self, index: int):
        largest = index
        left = 2 * index + 1
        right = 2 * index + 2
        
        if left < len(self.heap) and self.heap[left][0] > self.heap[largest][0]:
            largest = left
            
        if right < len(self.heap) and self.heap[right][0] > self.heap[largest][0]:
            largest = right
            
        if largest != index:
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            self._bubble_down(largest)

    def to_list(self):
        return [item[1] for item in sorted(self.heap, key=lambda x: -x[0])]
