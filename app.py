from flask import Flask, render_template, request, redirect
from models import Request
from matcher import add_request, get_next_request
from datastore import init_db

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

init_db()
RID = 1

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/seeker")
def seeker():
    return render_template("seeker_home.html")

@app.route("/volunteer")
def volunteer():
    return render_template("volunteer_home.html")

@app.route("/request", methods=["GET", "POST"])
def request_help():
    global RID
    if request.method == "POST":
        r = Request(
            RID,
            request.form["category"],
            request.form["description"],
            int(request.form["severity"])
        )
        RID += 1
        add_request(r)
        assigned = get_next_request()
        assigned.status = "ASSIGNED"
        return render_template("status.html", r=assigned)

    return render_template("request_form.html")

if __name__ == "__main__":
    app.run(debug=True)
