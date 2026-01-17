from flask import Flask, render_template, request
from models import User, Volunteer, Request
from datastore import volunteers
from request_handler import add_request
from matcher import match_volunteer

app = Flask(__name__)

# Dummy volunteers
volunteers.append(Volunteer("Nikitha", "btm", 5))
volunteers.append(Volunteer("Ravi", "jayanagar", 7))
volunteers.append(Volunteer("Anitha", "whitefield", 6))


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        location = request.form["location"]
        user = User(name, role, location)
        return render_template("request.html", user=user)
    return render_template("login.html")


@app.route("/status", methods=["POST"])
def status():
    requester = request.form["name"]
    location = request.form["location"]
    desc = request.form["description"]

    req = Request(requester, "General", desc, location)
    add_request(req)

    vol = match_volunteer(req, volunteers)
    if vol:
        req.assigned_volunteer = vol
        vol.available = False
        req.status = "ASSIGNED"

    return render_template("status.html", request=req, volunteer=vol)


if __name__ == "__main__":
    app.run(debug=True)
