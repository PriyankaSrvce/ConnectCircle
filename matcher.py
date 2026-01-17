import heapq
from collections import deque

normal_queue = deque()
emergency_heap = []
request_map = {}

def is_emergency(category, severity):
    return category in ["Medical", "Safety"] or severity >= 4

def add_request(req):
    request_map[req.id] = req
    if is_emergency(req.category, req.severity):
        heapq.heappush(emergency_heap, (-req.severity, req))
    else:
        normal_queue.append(req)

def get_next_request():
    if emergency_heap:
        return heapq.heappop(emergency_heap)[1]
    if normal_queue:
        return normal_queue.popleft()
    return None
