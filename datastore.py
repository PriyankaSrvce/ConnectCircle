# ================================
# ConnectCircle - Central Datastore
# ================================

from collections import deque
import heapq

# ----------------
# GLOBAL DATA STORES
# ----------------

# HashMaps (Dictionaries)
users = {}          # user_id -> User
volunteers = {}     # volunteer_id -> Volunteer
requests = {}       # request_id -> Request

# ----------------
# REQUEST QUEUES (Member 2 logic)
# ----------------

# Normal requests (FIFO Queue)
normal_queue = deque()

# Emergency requests (Priority Queue)
# Stored as (-severity, request)
emergency_pq = []

# ----------------
# REQUEST HISTORY (Linked List concept)
# ----------------

# Using list to represent append-only linked list
request_history = []

# ----------------
# GRAPH STRUCTURE (for matcher)
# ----------------

# Adjacency list: location -> list of (neighbor, distance)
community_graph = {}

# ----------------
# HELPER FUNCTIONS
# ----------------

def add_user(user):
    users[user.user_id] = user


def add_volunteer(volunteer):
    volunteers[volunteer.user_id] = volunteer


def add_request(request, is_emergency=False):
    requests[request.request_id] = request

    if is_emergency:
        heapq.heappush(emergency_pq, (-request.severity, request))
    else:
        normal_queue.append(request)


def get_next_request():
    if emergency_pq:
        _, req = heapq.heappop(emergency_pq)
        return req
    elif normal_queue:
        return normal_queue.popleft()
    return None


def add_to_history(request):
    request_history.append(request)


def add_edge(loc1, loc2, distance):
    if loc1 not in community_graph:
        community_graph[loc1] = []
    if loc2 not in community_graph:
        community_graph[loc2] = []

    community_graph[loc1].append((loc2, distance))
    community_graph[loc2].append((loc1, distance))
