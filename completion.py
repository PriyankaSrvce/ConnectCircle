from datastore import history

def complete_request(request, success=True):
    request.status = "COMPLETED"
    if success and request.assigned_volunteer:
        request.assigned_volunteer.trust += 1
    history.append(request)
