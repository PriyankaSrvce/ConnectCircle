from flask import Flask, render_template, request, redirect
from models import Request
from datastore import request_counter
from request_handler import add_request
from matcher import match_volunteer
from completion import complete_request
import datastore

app = Flask(__name__)

current_request = None

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form["role"]
        if role == "seeker":
            return redirect("/request")
        else:
            return redirect("/volunteer")
    return render_template("login.html")


@app.route("/request", methods=["GET", "POST"])
def seeker_request():
    global current_request
    if request.method == "POST":
        desc = request.form["desc"]
        category = request.form["category"]
        location = request.form["location"]

        req = Request(
            datastore.request_counter,
            "User",
            category,
            desc,
            location
        )
        datastore.request_counter += 1
        add_request(req)

        vol = match_volunteer()
        if vol:
            req.volunteer = vol.name
            req.status = "ASSIGNED"

        current_request = req
        return redirect("/status")

    return render_template("seeker_request.html")


@app.route("/status", methods=["GET", "POST"])
def status():
    global current_request
    if request.method == "POST":
        rating = int(request.form["rating"])
        complete_request(current_request, rating)
    return render_template("status.html", req=current_request)


@app.route("/volunteer")
def volunteer_dashboard():
    return render_template("volunteer_dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
