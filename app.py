from flask import Flask, render_template, request, redirect, url_for
import os
from database import init_db, get_connection

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

init_db()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, role) VALUES (?,?)", (name, role))
        user_id = cur.lastrowid
        conn.commit()
        conn.close()

        if role == "seeker":
            return redirect(url_for("home", user_id=user_id))
        else:
            return redirect(url_for("volunteer_dashboard", user_id=user_id))

    return render_template("login.html")

# ---------------- HOME ----------------
@app.route("/home/<int:user_id>")
def home(user_id):
    return render_template("home.html", user_id=user_id)

# ---------------- CREATE REQUEST ----------------
@app.route("/create/<int:user_id>", methods=["GET", "POST"])
def create_request(user_id):
    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]

        image = request.files["image"]
        image_path = ""
        if image:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
            image.save(image_path)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO requests (user_id, category, description, image, status)
            VALUES (?,?,?,?,?)
        """, (user_id, category, description, image_path, "REQUESTED"))
        req_id = cur.lastrowid
        conn.commit()
        conn.close()

        return redirect(url_for("tracking", request_id=req_id))

    return render_template("create_request.html", user_id=user_id)

# ---------------- TRACKING ----------------
@app.route("/tracking/<int:request_id>")
def tracking(request_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM requests WHERE id=?", (request_id,))
    status = cur.fetchone()[0]
    conn.close()
    return render_template("tracking.html", status=status, request_id=request_id)

# ---------------- VOLUNTEER DASHBOARD ----------------
@app.route("/volunteer/<int:user_id>")
def volunteer_dashboard(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, category, description FROM requests WHERE status='REQUESTED'")
    requests_list = cur.fetchall()
    conn.close()
    return render_template("volunteer_dashboard.html", requests=requests_list, user_id=user_id)

# ---------------- ACCEPT REQUEST ----------------
@app.route("/accept/<int:request_id>/<int:volunteer_id>")
def accept(request_id, volunteer_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE requests SET status='ON THE WAY', volunteer_id=?
        WHERE id=?
    """, (volunteer_id, request_id))
    conn.commit()
    conn.close()
    return redirect(url_for("tracking", request_id=request_id))

# ---------------- COMPLETE ----------------
@app.route("/complete/<int:request_id>")
def complete(request_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE requests SET status='COMPLETED' WHERE id=?", (request_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("rating", request_id=request_id))

# ---------------- RATING ----------------
@app.route("/rating/<int:request_id>", methods=["GET", "POST"])
def rating(request_id):
    if request.method == "POST":
        rating = request.form["rating"]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO ratings (request_id, rating) VALUES (?,?)", (request_id, rating))
        conn.commit()
        conn.close()
        return "Thank you! Help completed successfully."

    return render_template("rating.html", request_id=request_id)

if __name__ == "__main__":
    app.run(debug=True)
