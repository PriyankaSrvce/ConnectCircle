class Request:
    def __init__(self, rid, category, description, severity):
        self.id = rid
        self.category = category
        self.description = description
        self.severity = severity
        self.status = "PENDING"
        self.volunteer = None
