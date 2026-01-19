from flask import Flask, render_template, request, redirect, session
from data import users, requests, PriorityQueue
from emergency import classify_emergency

app = Flask(__name__)
app.secret_key = "secret123"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        for u in users:
            if u["username"] == request.form["username"] and u["password"] == request.form["password"]:
                session["user"] = u
                return redirect("/seeker" if u["role"] == "Seeker" else "/volunteer")
        return "Invalid credentials"
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users.append({
            "username": request.form["username"],
            "password": request.form["password"],
            "role": request.form["role"]
        })
        return redirect("/")
    return render_template("signup.html")


@app.route("/seeker", methods=["GET", "POST"])
def seeker():
    user = session.get("user")
    if request.method == "POST":
        emergency = classify_emergency(
            request.form["category"],
            request.form["description"]
        )
        requests.append({
            "seeker": user["username"],
            "category": request.form["category"],
            "description": request.form["description"],
            "location": request.form["location"],
            "status": "Pending",
            "priority": 1 if emergency else 0,
            "volunteer": None,
            "phone": None,
            "eta": None
        })
    my_requests = [r for r in requests if r["seeker"] == user["username"]]
    return render_template("seeker_dashboard.html", requests=my_requests)


@app.route("/volunteer", methods=["GET", "POST"])
def volunteer():
    pq = PriorityQueue()
    for r in requests:
        if r["status"] == "Pending":
            pq.enqueue(r, r["priority"])
    return render_template("volunteer_dashboard.html", requests=pq.get_all())


@app.route("/accept", methods=["POST"])
def accept():
    for r in requests:
        if r["seeker"] == request.form["seeker"]:
            r["status"] = "Accepted"
            r["volunteer"] = session["user"]["username"]
            r["phone"] = request.form["phone"]
            r["eta"] = request.form["eta"]
    return redirect("/volunteer")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
