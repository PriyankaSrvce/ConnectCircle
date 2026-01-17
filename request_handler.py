from datastore import request_queue, requests

def add_request(req):
    request_queue.append(req)
    requests[req.req_id] = req
