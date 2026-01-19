from flask import Flask, render_template, request, redirect, session
import sqlite3, os, heapq, time, math
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "connectcircle-secret"

DB = "database.db"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- DATABASE ----------
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
        priority INTEGER,
        status TEXT,
        image TEXT,
        assigned_volunteer INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- HELPERS ----------
def haversine(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return float("inf")
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def classify_priority(category, description):
    urgent_words = ["urgent", "pain", "fell", "bleeding", "help fast"]
    score = sum(1 for w in urgent_words if w in description.lower())
    if category in ["Medical", "Safety"] or score >= 2:
        return 1   # Emergency
    return 2       # Normal

# ---------- AUTH ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        if not user or not check_password_hash(user["password"], password):
            return "Invalid credentials"

        session["user_id"] = user["id"]
        session["role"] = user["role"]

        return redirect("/seeker" if user["role"] == "Seeker" else "/volunteer")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("""
            INSERT INTO users (username, email, password, role)
            VALUES (?, ?, ?, ?)
            """, (username, email, password, role))
            conn.commit()
        except:
            return "User already exists"

        return redirect("/")

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- SEEKER ----------
@app.route("/seeker", methods=["GET", "POST"])
def seeker():
    if session.get("role") != "Seeker":
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]

        image = request.files.get("image")
        filename = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))

        priority = classify_priority(category, description)

        cur.execute("""
        INSERT INTO requests
        (seeker_id, category, description, priority, status, image)
        VALUES (?, ?, ?, ?, 'Pending', ?)
        """, (session["user_id"], category, description, priority, filename))
        conn.commit()

    cur.execute("""
    SELECT * FROM requests WHERE seeker_id=?
    """, (session["user_id"],))
    requests = cur.fetchall()

    return render_template("seeker_dashboard.html", requests=requests)

# ---------- VOLUNTEER ----------
@app.route("/volunteer")
def volunteer():
    if session.get("role") != "Volunteer":
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM requests WHERE status='Pending'
    """)
    rows = cur.fetchall()

    pq = []
    for r in rows:
        heapq.heappush(pq, (r["priority"], r["id"], r))

    ordered = [heapq.heappop(pq)[2] for _ in range(len(pq))]
    return render_template("volunteer_dashboard.html", requests=ordered)

@app.route("/accept/<int:req_id>")
def accept(req_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    UPDATE requests
    SET status='Accepted', assigned_volunteer=?
    WHERE id=?
    """, (session["user_id"], req_id))
    conn.commit()
    return redirect("/volunteer")

@app.route("/complete/<int:req_id>")
def complete(req_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    UPDATE requests SET status='Completed'
    WHERE id=?
    """, (req_id,))
    conn.commit()
    return redirect("/volunteer")

if __name__ == "__main__":
    app.run(debug=True)
