class User:
    def __init__(self, user_id, name, role):
        self.user_id = user_id
        self.name = name
        self.role = role  # seeker / volunteer


class Volunteer(User):
    def __init__(self, user_id, name, location):
        super().__init__(user_id, name, "volunteer")
        self.location = location
        self.trust = 5
        self.available = True


class Request:
    def __init__(self, req_id, category, description, location, severity):
        self.req_id = req_id
        self.category = category
        self.description = description
        self.location = location
        self.severity = severity
        self.status = "PENDING"
        self.assigned_volunteer = None
