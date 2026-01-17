from datastore import volunteers

def match_volunteer():
    for v in volunteers.values():
        if v.available:
            v.available = False
            return v
    return None
