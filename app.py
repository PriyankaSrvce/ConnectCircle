from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from functools import wraps
import heapq

app = Flask(__name__)
app.secret_key = "connectcircle_secret"

DB = "database.db"

# ---------------- DB SETUP ----------------
def get_db():
    return sqlite3.connect(DB)

def init_db():
    con = get_db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seeker TEXT,
        category TEXT,
        description TEXT,
        location TEXT,
        priority INTEGER,
        status TEXT,
        volunteer TEXT,
        phone TEXT,
        eta TEXT
    )
    """)

    con.commit()
    con.close()

init_db()

# ---------------- AUTH DECORATOR ----------------
def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if "user" not in session:
                return redirect("/")
            if role and session["role"] != role:
                return redirect("/")
            return fn(*args, **kwargs)
        return decorated
    return wrapper

# ---------------- LOGIN / SIGNUP ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p))
        row = cur.fetchone()
        con.close()

        if row:
            session["user"] = u
            session["role"] = row[0]
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        r = request.form["role"]

        con = get_db()
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO users VALUES (NULL,?,?,?)", (u, p, r))
            con.commit()
        except:
            return "User already exists"
        con.close()
        return redirect("/")

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- DASHBOARD ROUTER ----------------
@app.route("/dashboard")
def dashboard():
    if session["role"] == "seeker":
        return redirect("/seeker")
    return redirect("/volunteer")

# ---------------- SEEKER ----------------
@app.route("/seeker", methods=["GET", "POST"])
@login_required("seeker")
def seeker():
    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        cat = request.form["category"]
        desc = request.form["description"]
        loc = request.form["location"]

        # Emergency logic
        priority = 0
        urgent_words = ["pain", "urgent", "help", "accident"]
        if cat.lower() in ["medical", "safety"] or sum(w in desc.lower() for w in urgent_words) >= 2:
            priority = 1

        cur.execute("""
        INSERT INTO requests VALUES (NULL,?,?,?,?,?,?,?,?)
        """, (session["user"], cat, desc, loc, priority,
              "Pending", None, None, None))
        con.commit()

    cur.execute("SELECT * FROM requests WHERE seeker=?", (session["user"],))
    data = cur.fetchall()
    con.close()

    return render_template("seeker_dashboard.html", requests=data)

# ---------------- VOLUNTEER ----------------
@app.route("/volunteer", methods=["GET", "POST"])
@login_required("volunteer")
def volunteer():
    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        rid = request.form["rid"]
        phone = request.form["phone"]
        eta = request.form["eta"]

        cur.execute("""
        UPDATE requests
        SET status='Accepted', volunteer=?, phone=?, eta=?
        WHERE id=?
        """, (session["user"], phone, eta, rid))
        con.commit()

    cur.execute("SELECT * FROM requests WHERE status='Pending'")
    rows = cur.fetchall()
    con.close()

    # Priority Queue (DSA)
    pq = []
    for r in rows:
        heapq.heappush(pq, (-r[5], r))

    ordered = [heapq.heappop(pq)[1] for _ in range(len(pq))]
    return render_template("volunteer_dashboard.html", requests=ordered)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
