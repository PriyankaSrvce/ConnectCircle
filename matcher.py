from collections import deque
from datastore import graph

def bfs(start):
    visited = set()
    queue = deque([(start, 0)])
    distances = {}

    while queue:
        node, dist = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        distances[node] = dist

        for nxt in graph.get(node, []):   # SAFE ACCESS
            if nxt not in visited:
                queue.append((nxt, dist + 1))

    return distances


def match_volunteer(request, volunteers):
    distances = bfs(request.location)

    best = None
    best_score = -1

    for v in volunteers:
        if not v.available:
            continue
        dist = distances.get(v.location, 999)
        score = v.trust * 10 - dist
        if score > best_score:
            best = v
            best_score = score

    return best
