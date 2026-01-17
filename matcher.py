from collections import deque

# Graph (Adjacency List)
graph = {
    "BTM": ["Jayanagar"],
    "Jayanagar": ["BTM", "Whitefield"],
    "Whitefield": ["Jayanagar"]
}

def bfs(start):
    dist = {node: float("inf") for node in graph}
    dist[start] = 0
    q = deque([start])

    while q:
        cur = q.popleft()
        for nxt in graph[cur]:
            if dist[nxt] == float("inf"):
                dist[nxt] = dist[cur] + 1
                q.append(nxt)
    return dist


def match_volunteer(request, volunteers):
    distances = bfs(request.location)
    best = None
    best_score = -1

    for v in volunteers.values():
        if not v.available:
            continue
        d = distances.get(v.location, 10)
        score = v.trust * 10 - d
        if score > best_score:
            best_score = score
            best = v

    return best
