import heapq

URGENT_KEYWORDS = ["urgent", "pain", "fell", "help", "fast"]

def classify_request(category, description, nearby_volunteers):
    emergency = 0

    if category.lower() in ["medical", "safety", "mobility"]:
        emergency += 1

    count = sum(word in description.lower() for word in URGENT_KEYWORDS)
    if count >= 2:
        emergency += 1

    if not nearby_volunteers:
        emergency += 1

    return 0 if emergency >= 2 else 1   # 0 = Emergency, 1 = Normal


class RequestQueue:
    def __init__(self):
        self.heap = []

    def add(self, priority, request_id):
        heapq.heappush(self.heap, (priority, request_id))

    def pop(self):
        return heapq.heappop(self.heap) if self.heap else None
