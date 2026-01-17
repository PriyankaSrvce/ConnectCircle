from collections import deque
from models import Volunteer

requests = {}
request_queue = deque()

volunteers = {
    "Ravi": Volunteer("Ravi"),
    "Anitha": Volunteer("Anitha"),
    "Nikitha": Volunteer("Nikitha")
}

request_counter = 1
