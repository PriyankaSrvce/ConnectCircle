# ================================
# ConnectCircle - Main Application
# ================================

from flask import Flask, render_template, request, redirect, url_for

from models import Request
from request_handler import add_request, get_next_request
from datastore import volunteers, requests
from completion import complete_request, reject_request

app = Flask(__name__)

# ----------------
# HOME PAGE
# ----------------
@app.route("/")
def home():
    return render_template("request.html")


# ----------------
# SUBMIT REQUEST
# ----------------
@app.route("/submit_request", methods=["POST"])
def submit_request():
    req_id = len(requests) + 1
    category = request.form["category"]
    description = request.form["description"]
    location = request.form["location"]

    new_request = Request(
        request_id=req_id,
        category=category,
        description=description,
        location=location,
        severity=1
    )

    requests[req_id] = new_request
    add_request(new_request)

    return redirect(url_for("request_status", req_id=req_id))


# ----------------
# REQUEST STATUS
# ----------------
@app.route("/status/<int:req_id>")
def request_status(req_id):
    req = requests.get(req_id)
    return render_template("status.html", request=req)


# ----------------
# COMPLETE REQUEST
# ----------------
@app.route("/complete/<int:req_id>")
def complete(req_id):
    req = requests.get(req_id)
    if req:
        complete_request(req)
    return redirect(url_for("home"))


# ----------------
# REJECT REQUEST
# ----------------
@app.route("/reject/<int:req_id>")
def reject(req_id):
    req = requests.get(req_id)
    if req:
        reject_request(req)
    return redirect(url_for("home"))


# ----------------
# RUN SERVER
# ----------------
if __name__ == "__main__":
    app.run(debug=True)
