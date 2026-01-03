# ================================
# ConnectCircle - Member 2
# Request Processing & Queue Management
# ================================

import heapq
from collections import deque


# ----------------
# REQUEST OBJECT
# ----------------
class Request:
    def __init__(self, request_id, category, description, location, severity):
        self.request_id = request_id
        self.category = category
        self.description = description
        self.location = location
        self.severity = severity
        self.status = "PENDING"

    def __str__(self):
        return f"Request({self.request_id}, {self.category}, {self.status})"


# ----------------
# DATA STRUCTURES
# ----------------

# HashMap to store all requests
request_map = {}

# Queue for normal requests (FIFO)
normal_queue = deque()

# Priority Queue (Heap) for emergency requests
# (-severity is used to convert min-heap to max-heap)
emergency_pq = []


# ----------------
# EMERGENCY CLASSIFICATION
# ----------------
def is_emergency(request):
    # Rule 1: Category-based emergency
    emergency_categories = ["Medical", "Safety", "Mobility"]
    if request.category in emergency_categories:
        return True

    # Rule 2: Keyword-based urgency (refined)
    urgent_keywords = [
        "urgent",
        "severe",
        "pain",
        "emergency",
        "fell",
        "can't move",
        "cannot move"
    ]

    description_lower = request.description.lower()
    for word in urgent_keywords:
        if word in description_lower:
            return True

    return False


# ----------------
# ADD REQUEST
# ----------------
def add_request(request):
    # Store request in HashMap
    request_map[request.request_id] = request

    # Insert into appropriate data structure
    if is_emergency(request):
        heapq.heappush(emergency_pq, (-request.severity, request))
        print(f"Request {request.request_id} added to EMERGENCY priority queue")
    else:
        normal_queue.append(request)
        print(f"Request {request.request_id} added to NORMAL queue")


# ----------------
# SCHEDULER LOGIC
# ----------------
def get_next_request():
    if len(emergency_pq) > 0:
        _, req = heapq.heappop(emergency_pq)
        return req
    elif len(normal_queue) > 0:
        return normal_queue.popleft()
    else:
        return None


# ----------------
# TESTING / DEMO
# ----------------
if __name__ == "__main__":
    # Sample requests
    r1 = Request(
        1,
        "Household",
        "Need groceries from nearby store",
        "Block A",
        1
    )

    r2 = Request(
        2,
        "Medical",
        "I fell down and have severe pain",
        "Block B",
        5
    )

    r3 = Request(
        3,
        "Safety",
        "Emergency situation in my area",
        "Block C",
        4
    )

    # Add requests
    add_request(r1)
    add_request(r2)
    add_request(r3)

    print("\n--- Scheduler Output ---")
    next_req = get_next_request()
    if next_req:
        print("Next request served:", next_req)
    else:
        print("No requests available")

