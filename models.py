# ================================
# ConnectCircle - Models
# ================================

class User:
    def __init__(self, user_id, name, location):
        self.user_id = user_id
        self.name = name
        self.location = location


class Volunteer(User):
    def __init__(self, user_id, name, location, profession):
        super().__init__(user_id, name, location)
        self.profession = profession
        self.trust_score = 5      # Default trust (0–10)
        self.available = True

    def increase_trust(self):
        if self.trust_score < 10:
            self.trust_score += 1

    def decrease_trust(self):
        if self.trust_score > 0:
            self.trust_score -= 1


class Request:
    def __init__(self, request_id, requester_name, category, description, location, severity):
        self.request_id = request_id
        self.requester_name = requester_name
        self.category = category
        self.description = description
        self.location = location
        self.severity = severity
        self.status = "PENDING"     # PENDING | ASSIGNED | COMPLETED
        self.assigned_volunteer = None
