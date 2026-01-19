from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "connectcircle-secret"

UPLOAD_FOLDER = "static/uploads"
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DATA STRUCTURES ----------------

users = {}          # username -> {password, role, email}
emails = set()      # to prevent duplicate emails
requests_db = []
volunteer_ratings = {}
request_id = 1

# ---------------- HELPERS ----------------

def emergency_classifier(req):
    score = 0
    if req["category"] == "Medical":
        score += 3
    keywords = ["urgent", "emergency", "accident", "critical", "bleeding"]
    if any(k in req["description"].lower() for k in keywords):
        score += 2
    active = sum(1 for r in requests_db if r["status"] == "Accepted")
    total_vol = sum(1 for u in users.values() if u["role"] == "Volunteer")
    if total_vol - active <= 1:
        score += 1
    return ("Emergency" if score >= 4 else "Normal", score)


def change_state(req, new):
    transitions = {
        "Pending": ["Accepted"],
        "Accepted": ["Completed"],
        "Completed": ["Rated"]
    }
    if new in transitions.get(req["status"], []):
        req["status"] = new

# ---------------- AUTH ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in users and users[u]["password"] == p:
            session["user"] = u
            session["role"] = users[u]["role"]
            return redirect("/seeker" if users[u]["role"] == "Seeker" else "/volunteer")
        return "Invalid credentials"
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        e = request.form["email"]

        if u in users or e in emails:
            return "User already exists"

        users[u] = {
            "password": request.form["password"],
            "role": request.form["role"],
            "email": e
        }
        emails.add(e)
        return redirect("/")
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- SEEKER ----------------

@app.route("/seeker", methods=["GET", "POST"])
def seeker():
    global request_id
    if session.get("role") != "Seeker":
        return redirect("/")

    if request.method == "POST":
        img = request.files.get("image")
        img_path = None
        if img and img.filename:
            img_path = os.path.join(app.config["UPLOAD_FOLDER"], img.filename)
            img.save(img_path)

        req = {
            "id": request_id,
            "seeker": session["user"],
            "seeker_phone": request.form["phone"],
            "seeker_location": request.form["location"],
            "category": request.form["category"],
            "description": request.form["description"],
            "image": img_path,
            "status": "Pending",
            "urgency": None,
            "priority": 0,
            "volunteer": None,
            "vol_phone": None,
            "vol_location": None,
            "eta": None,
            "rating": None,
            "time": datetime.now()
        }

        req["urgency"], req["priority"] = emergency_classifier(req)
        requests_db.append(req)
        request_id += 1

    my_requests = [r for r in requests_db if r["seeker"] == session["user"]]
    return render_template("seeker.html", requests=my_requests, user=session["user"])

# ---------------- VOLUNTEER ----------------

@app.route("/volunteer", methods=["GET", "POST"])
def volunteer():
    if session.get("role") != "Volunteer":
        return redirect("/")

    if request.method == "POST":
        rid = int(request.form["id"])
        for r in requests_db:
            if r["id"] == rid and r["status"] == "Pending":
                r["volunteer"] = session["user"]
                r["vol_phone"] = request.form["phone"]
                r["vol_location"] = request.form["location"]
                r["eta"] = request.form["eta"]
                change_state(r, "Accepted")

    pending = sorted(
        [r for r in requests_db if r["status"] == "Pending"],
        key=lambda x: x["priority"],
        reverse=True
    )

    mine = [r for r in requests_db if r["volunteer"] == session["user"]]
    return render_template("volunteer.html", pending=pending, mine=mine, user=session["user"])


@app.route("/complete/<int:rid>")
def complete(rid):
    for r in requests_db:
        if r["id"] == rid:
            change_state(r, "Completed")
    return redirect("/volunteer")


@app.route("/rate/<int:rid>", methods=["POST"])
def rate(rid):
    rating = int(request.form["rating"])
    for r in requests_db:
        if r["id"] == rid:
            r["rating"] = rating
            change_state(r, "Rated")
            volunteer_ratings.setdefault(r["volunteer"], []).append(rating)
    return redirect("/seeker")


if __name__ == "__main__":
    app.run(debug=True)
