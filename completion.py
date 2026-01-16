# ================================
# ConnectCircle - Completion Logic
# ================================

from datastore import (
    volunteers,
    add_to_history,
    get_next_request
)

# ----------------
# MARK REQUEST COMPLETED
# ----------------
def complete_request(request):
    request.status = "COMPLETED"

    if request.assigned_volunteer:
        volunteer = volunteers.get(request.assigned_volunteer)
        if volunteer:
            volunteer.increase_trust()

    add_to_history(request)
    print(f"Request {request.request_id} completed and archived")


# ----------------
# VOLUNTEER REJECTS REQUEST
# ----------------
def reject_request(request):
    print(
        f"Volunteer {request.assigned_volunteer} rejected request {request.request_id}"
    )

    volunteer = volunteers.get(request.assigned_volunteer)
    if volunteer:
        volunteer.decrease_trust()
        volunteer.available = True

    request.assigned_volunteer = None
    request.status = "PENDING"

    # Try reassignment
    next_request = get_next_request()
    return next_request
