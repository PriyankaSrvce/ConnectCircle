from datastore import volunteers

def complete_request(req, rating):
    vol = volunteers[req.volunteer]
    vol.trust = min(10, vol.trust + rating)
    vol.available = True
    req.status = "COMPLETED"
