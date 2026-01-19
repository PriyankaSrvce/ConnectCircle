# requests_logic.py
from models import HelpRequest

EMERGENCY_CATEGORIES = ["Medical", "Safety", "Mobility"]
URGENT_KEYWORDS = ["urgent", "emergency", "bleeding", "accident", "critical"]

def classify_request(category, description):
    score = 0

    if category in EMERGENCY_CATEGORIES:
        score += 1

    matches = sum(1 for k in URGENT_KEYWORDS if k in description.lower())
    if matches >= 2:
        score += 1

    return 1 if score > 0 else 0
