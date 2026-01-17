from collections import deque

# Requests
normal_queue = deque()
history = []

# Volunteers
volunteers = []

# Location Graph (FIXED)
graph = {
    "btm": ["jayanagar", "iblur"],
    "jayanagar": ["btm", "whitefield"],
    "iblur": ["btm"],
    "whitefield": ["jayanagar"]
}
