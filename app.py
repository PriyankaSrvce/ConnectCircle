from flask import Flask, render_template, request, redirect
from database import init_db, get_db
from matcher import classify_request, RequestQueue

app = Flask(__name__)
queue = RequestQueue()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/seeker", methods=["GET", "POST"])
def seeker():
    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]

        priority = classify_request(category, description, nearby_volunteers=[1])
        db = get_db()
        cur = db.execute(
            "INSERT INTO requests (category, description, priority, status) VALUES (?, ?, ?, ?)",
            (category, description, priority, "Pending")
        )
        db.commit()

        queue.add(priority, cur.lastrowid)
        return redirect("/status")

    return render_template("seeker_request.html")

@app.route("/status")
def status():
    return render_template("seeker_status.html")

@app.route("/volunteer")
def volunteer():
    db = get_db()
    requests = db.execute(
        "SELECT * FROM requests ORDER BY priority"
    ).fetchall()
    return render_template("volunteer_dashboard.html", requests=requests)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
