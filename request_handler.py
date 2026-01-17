import heapq
from datastore import normal_queue, emergency_pq, requests

def is_emergency(request):
    keywords = ["urgent", "emergency", "pain", "fell"]
    if request.category.lower() in ["medical", "safety"]:
        return True
    for word in keywords:
        if word in request.description.lower():
            return True
    return False


def add_request(request):
    requests[request.req_id] = request
    if is_emergency(request):
        heapq.heappush(emergency_pq, (-request.severity, request))
    else:
        normal_queue.append(request)


def get_next_request():
    if emergency_pq:
        return heapq.heappop(emergency_pq)[1]
    if normal_queue:
        return normal_queue.popleft()
    return None
