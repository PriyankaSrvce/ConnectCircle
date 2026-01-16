# ================================
# ConnectCircle - Volunteer Matcher
# ================================

from collections import deque

from datastore import volunteers

# ----------------
# GRAPH (Adjacency List)
# ----------------
community_graph = {
    "BTM": ["Jayanagar"],
    "Jayanagar": ["BTM", "JP Nagar"],
    "JP Nagar": ["Jayanagar", "Whitefield"],
    "Whitefield": ["JP Nagar"]
}

# ----------------
# BFS FOR NEAREST LOCATION
# ----------------
def bfs_distance(start):
    distance = {start: 0}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for neighbor in community_graph.get(current, []):
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)

    return distance


# ----------------
# MATCH BEST VOLUNTEER
# ----------------
def find_best_volunteer(request):
    distances = bfs_distance(request.location)

    best_volunteer = None
    best_score = -1

    for volunteer in volunteers.values():
        if not volunteer.available:
            continue

        if volunteer.location not in distances:
            continue

        # Trust-based + distance-based scoring
        score = (volunteer.trust * 10) - distances[volunteer.location]

        if score > best_score:
            best_score = score
            best_volunteer = volunteer

    if best_volunteer:
        best_volunteer.available = False
        request.assigned_volunteer = best_volunteer.user_id
        request.status = "ASSIGNED"

    return best_volunteer
