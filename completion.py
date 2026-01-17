from datastore import history

def complete_request(request, success=True):
    if success:
        request.status = "COMPLETED"
        if request.assigned_volunteer:
            request.assigned_volunteer.trust += 1
    else:
        request.status = "FAILED"

    history.append(request)
