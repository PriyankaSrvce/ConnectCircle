from datastore import normal_queue

def add_request(request):
    normal_queue.append(request)

def get_next_request():
    if normal_queue:
        return normal_queue.popleft()
    return None

