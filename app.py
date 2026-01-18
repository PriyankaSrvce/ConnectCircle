from flask import Flask, render_template, request, redirect, session
import sqlite3, os, heapq, time, math
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "connectcircle-secret"

DB = "database.db"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT,
        password TEXT,
        role TEXT,
        latitude REAL,
        longitude REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seeker_id INTEGER,
        category TEXT,
        description TEXT,
        priority TEXT,
        location TEXT,
        status TEXT,
        assigned_volunteer INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        if not user:
            return "User does not exist. Please Sign Up first."

        if not check_password_hash(user["password"], password):
            return "Incorrect password"

        session["user_id"] = user["id"]
        session["role"] = user["role"]

        return redirect("/seeker" if user["role"] == "Seeker" else "/volunteer")

    return render_template("login.html")

# ---------------- SIGN UP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        hashed_pw = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        if cur.fetchone():
            return "Username already exists"

        cur.execute("""
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
        """, (username, email, hashed_pw, role))

        conn.commit()
        return redirect("/")

    return render_template("signup.html")

# ---------------- SEEKER ----------------
@app.route("/seeker")
def seeker():
    if "user_id" not in session:
        return redirect("/")
    return "Seeker dashboard (already works in your app)"

# ---------------- VOLUNTEER ----------------
@app.route("/volunteer")
def volunteer():
    if "user_id" not in session:
        return redirect("/")
    return "Volunteer dashboard (already works in your app)"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
