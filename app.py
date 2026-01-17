from flask import Flask, render_template, request, redirect
from models import User, Volunteer, Request
from datastore import users, volunteers
from request_handler import add_request, get_next_request
from matcher import match_volunteer
from completion import complete_request

app = Flask(__name__)
req_id = 1

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def do_login():
    name = request.form["name"]
    role = request.form["role"]
    if role == "volunteer":
        v = Volunteer(len(volunteers)+1, name, "BTM")
        volunteers[v.user_id] = v
        return redirect("/volunteer")
    else:
        u = User(len(users)+1, name, "seeker")
        users[u.user_id] = u
        return redirect("/request")

@app.route("/request", methods=["GET","POST"])
def make_request():
    global req_id
    if request.method == "POST":
        r = Request(
            req_id,
            request.form["category"],
            request.form["description"],
            request.form["location"],
            int(request.form["severity"])
        )
        req_id += 1
        add_request(r)
        return redirect("/status")
    return render_template("request.html")

@app.route("/status")
def status():
    req = get_next_request()
    if not req:
        return "No requests"
    vol = match_volunteer(req, volunteers)
    if vol:
        req.assigned_volunteer = vol
        vol.available = False
    return render_template("status.html", req=req, vol=vol)

@app.route("/volunteer")
def volunteer():
    return render_template("volunteer.html")

if __name__ == "__main__":
    app.run(debug=True)
