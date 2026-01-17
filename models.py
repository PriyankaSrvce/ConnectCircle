class User:
    def __init__(self, user_id, name, role):
        self.user_id = user_id
        self.name = name
        self.role = role  # seeker / volunteer


class Request:
    def __init__(self, req_id, seeker, category, desc, location, image=None):
        self.req_id = req_id
        self.seeker = seeker
        self.category = category
        self.desc = desc
        self.location = location
        self.image = image
        self.status = "SEARCHING"
        self.volunteer = None


class Volunteer:
    def __init__(self, name):
        self.name = name
        self.trust = 5
        self.available = True
