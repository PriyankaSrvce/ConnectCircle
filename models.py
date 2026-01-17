class User:
    def __init__(self, name, role, location):
        self.name = name
        self.role = role  # "seeker" or "volunteer"
        self.location = location


class Volunteer(User):
    def __init__(self, name, location, trust=5):
        super().__init__(name, "volunteer", location)
        self.trust = trust
        self.available = True


class Request:
    def __init__(self, requester, category, description, location):
        self.requester = requester
        self.category = category
        self.description = description
        self.location = location
        self.status = "PENDING"
        self.assigned_volunteer = None
