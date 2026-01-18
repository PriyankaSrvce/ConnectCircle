from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "connectcircle_secret"

# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seeker_name TEXT,
        category TEXT,
        description TEXT,
        location TEXT,
        image TEXT,
        status TEXT,
        volunteer_name TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, role) VALUES (?, ?)", (name, role))
        conn.commit()
        conn.close()

        session["name"] = name
        session["role"] = role

        if role == "seeker":
            return redirect(url_for("seeker_home"))
        else:
            return redirect(url_for("volunteer_dashboard"))

    return render_template("login.html")

# ---------- SEEKER ----------
@app.route("/seeker")
def seeker_home():
    return render_template("seeker_home.html")

@app.route("/request-help", methods=["GET", "POST"])
def request_help():
    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]
        location = request.form["location"]

        image_file = request.files.get("image")
        image_name = None

        if image_file and image_file.filename:
            image_name = image_file.filename
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO requests
            (seeker_name, category, description, location, image, status, volunteer_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session["name"],
            category,
            description,
            location,
            image_name,
            "Pending",
            None
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("request_status"))

    return render_template("request_help.html")

@app.route("/status")
def request_status():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM requests
        WHERE seeker_name = ?
        ORDER BY id DESC LIMIT 1
    """, (session["name"],))
    req = cur.fetchone()
    conn.close()

    return render_template("status.html", req=req)

# ---------- VOLUNTEER ----------
@app.route("/volunteer")
def volunteer_dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM requests WHERE status='Pending'")
    requests = cur.fetchall()
    conn.close()

    return render_template("volunteer_dashboard.html", requests=requests)

@app.route("/accept/<int:req_id>")
def accept_request(req_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE requests
        SET status='Assigned', volunteer_name=?
        WHERE id=?
    """, (session["name"], req_id))
    conn.commit()
    conn.close()

    return redirect(url_for("volunteer_dashboard"))

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
