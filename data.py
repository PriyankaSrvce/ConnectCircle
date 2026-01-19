# data.py

class PriorityQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, item, priority):
        self.queue.append((priority, item))
        self.queue.sort(reverse=True)

    def get_all(self):
        return [item for _, item in self.queue]


# In‑memory storage (for demo / project)
users = []
requests = []
