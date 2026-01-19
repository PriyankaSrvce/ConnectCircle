# app.py
from flask import Flask, render_template, request, redirect, session
from models import PriorityQueue, HelpRequest
from auth import authenticate, register
from requests_logic import classify_request

app = Flask(__name__)
app.secret_key = "secret123"

pq = PriorityQueue()
all_requests = []

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = authenticate(request.form["username"], request.form["password"])
        if user:
            session["user"] = user.username
            session["role"] = user.role
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        register(
            request.form["username"],
            request.form["password"],
            request.form["role"]
        )
        return redirect("/")
    return render_template("signup.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if session["role"] == "Seeker":
        if request.method == "POST":
            priority = classify_request(
                request.form["category"],
                request.form["description"]
            )
            req = HelpRequest(
                session["user"],
                request.form["category"],
                request.form["description"],
                request.form["location"],
                priority
            )
            all_requests.append(req)
            pq.push(req)

        my_requests = [r for r in all_requests if r.seeker == session["user"]]
        return render_template("seeker_dashboard.html", requests=my_requests)

    else:
        pending = [r for r in pq.pop_all() if r.status == "Pending"]
        return render_template("volunteer_dashboard.html", requests=pending)

@app.route("/accept/<int:req_id>", methods=["POST"])
def accept(req_id):
    for r in all_requests:
        if r.id == req_id:
            r.status = "Accepted"
            r.volunteer = session["user"]
            r.phone = request.form["phone"]
            r.eta = request.form["eta"]
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
