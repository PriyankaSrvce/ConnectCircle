from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "connectcircle_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

# DO NOT crash if folder already exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DB ----------------
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

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

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
            return redirect(url_for("volunteer_home"))

    return render_template("login.html")

@app.route("/seeker")
def seeker_home():
    return "<h2>Seeker Home – next page coming</h2>"

@app.route("/volunteer")
def volunteer_home():
    return "<h2>Volunteer Home – next page coming</h2>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
