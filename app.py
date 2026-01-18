from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "connectcircle_secret"

# ---------------- BASIC CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

# Prevent folder crash
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT
    )
    """)

    # Requests table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seeker_name TEXT,
        category TEXT,
        description TEXT,
        image TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

# LOGIN PAGE (FIRST PAGE)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, role) VALUES (?, ?)",
            (name, role)
        )
        conn.commit()
        conn.close()

        session["name"] = name
        session["role"] = role

        if role == "seeker":
            return redirect(url_for("seeker_home"))
        else:
            return redirect(url_for("volunteer_home"))

    return render_template("login.html")


# ---------------- SEEKER FLOW ----------------

@app.route("/seeker")
def seeker_home():
    return render_template("seeker_home.html")


@app.route("/request-help", methods=["GET", "POST"])
def request_help():
    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]

        image_file = request.files.get("image")
        image_name = None

        if image_file and image_file.filename != "":
            image_name = image_file.filename
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
            image_file.save(image_path)

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO requests
            (seeker_name, category, description, image, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session.get("name"),
            category,
            description,
            image_name,
            "Pending"
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("request_status"))

    return render_template("request_help.html")


@app.route("/status")
def request_status():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM requests ORDER BY id DESC LIMIT 1"
    )
    req = cur.fetchone()
    conn.close()

    return render_template("status.html", req=req)


# ---------------- VOLUNTEER PLACEHOLDER ----------------

@app.route("/volunteer")
def volunteer_home():
    return "<h2>Volunteer Dashboard – coming next</h2>"


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
