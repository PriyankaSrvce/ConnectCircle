# emergency.py

def classify_emergency(category, description):
    emergency_categories = ["Medical", "Safety", "Mobility"]
    urgent_keywords = [
        "urgent", "emergency", "bleeding", "accident",
        "help", "critical", "severe", "pain"
    ]

    score = 0

    if category in emergency_categories:
        score += 1

    desc = description.lower()
    keyword_count = sum(1 for k in urgent_keywords if k in desc)
    if keyword_count >= 2:
        score += 1

    return score > 0
