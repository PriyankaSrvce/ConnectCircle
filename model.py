# models.py
import time
import heapq

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role


class HelpRequest:
    def __init__(self, seeker, category, description, location, priority):
        self.id = int(time.time() * 1000)
        self.seeker = seeker
        self.category = category
        self.description = description
        self.location = location
        self.priority = priority  # 1 = emergency, 0 = normal
        self.status = "Pending"
        self.volunteer = None
        self.phone = None
        self.eta = None
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    def __lt__(self, other):
        return self.priority > other.priority  # Priority Queue


class PriorityQueue:
    def __init__(self):
        self.queue = []

    def push(self, request):
        heapq.heappush(self.queue, request)

    def pop_all(self):
        return sorted(self.queue, reverse=True)
