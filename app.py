from flask import Flask, render_template, request, redirect, session
import sqlite3, os, heapq, time, math
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "connectcircle-secret"

DB = "database.db"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ================= DATABASE =================
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
        image TEXT,
        status TEXT,
        assigned_volunteer INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= DATA STRUCTURES =================
priority_queue = []
PRIORITY_MAP = {"Emergency": 1, "Normal": 2}

URGENT_KEYWORDS = [
    "urgent", "pain", "bleeding", "fell", "help fast", "emergency"
]

# ================= GRAPH / DISTANCE =================
def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def nearby_volunteer_exists(lat, lon):
    if lat is None or lon is None:
        return False

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT latitude, longitude FROM users WHERE role='Volunteer'")
    volunteers = cur.fetchall()

    for v in volunteers:
        if v["latitude"] and v["longitude"]:
            if distance(lat, lon, v["latitude"], v["longitude"]) <= 5:
                return True
    return False

# ================= EMERGENCY CLASSIFIER =================
def classify_priority(category, description, lat, lon):
    if category in ["Medical", "Safety", "Mobility"]:
        return "Emergency"

    count = sum(1 for k in URGENT_KEYWORDS if k in description.lower())
    if count >= 2:
        return "Emergency"

    if not nearby_volunteer_exists(lat, lon):
        return "Emergency"

    return "Normal"

# ================= LOGIN / SIGNUP =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        lat_raw = request.form.get("lat", "")
        lon_raw = request.form.get("lon", "")

        try:
            lat = float(lat_raw)
            lon = float(lon_raw)
        except ValueError:
            lat = None
            lon = None

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        # SIGN UP
        if "signup" in request.form:
            if user:
                return "User already exists"

            hashed = generate_password_hash(password)
            cur.execute("""
            INSERT INTO users (username, password, role, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
            """, (username, hashed, role, lat, lon))
            conn.commit()
            cur.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cur.fetchone()

        # LOGIN
        else:
            if not user or not check_password_hash(user["password"], password):
                return "Invalid credentials"

        session["user_id"] = user["id"]
        session["role"] = user["role"]

        return redirect("/seeker" if user["role"] == "Seeker" else "/volunteer")

    return render_template("login.html")

# ================= SEEKER =================
@app.route("/seeker", methods=["GET", "POST"])
def seeker():
    if "user_id" not in session:
        return redirect("/")

    seeker_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM requests WHERE seeker_id=?", (seeker_id,))
    existing = cur.fetchone()
    if existing:
        return render_template("seeker_status.html", req=existing)

    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]
        location = request.form["location"]

        image_path = None
        if "image" in request.files:
            img = request.files["image"]
            if img.filename:
                fname = secure_filename(img.filename)
                img.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
                image_path = fname

        cur.execute("SELECT latitude, longitude FROM users WHERE id=?", (seeker_id,))
        seeker = cur.fetchone()

        priority = classify_priority(
            category, description,
            seeker["latitude"], seeker["longitude"]
        )

        cur.execute("""
        INSERT INTO requests
        (seeker_id, category, description, priority, location, image, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending')
        """, (seeker_id, category, description, priority, location, image_path))

        conn.commit()
        req_id = cur.lastrowid
        heapq.heappush(priority_queue, (PRIORITY_MAP[priority], time.time(), req_id))

        return redirect("/seeker")

    return render_template("seeker_request.html")

# ================= VOLUNTEER =================
@app.route("/volunteer")
def volunteer():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT r.*, u.username AS seeker_name
    FROM requests r
    JOIN users u ON r.seeker_id = u.id
    WHERE r.status='Pending'
    ORDER BY CASE r.priority
        WHEN 'Emergency' THEN 1 ELSE 2 END
    """)
    data = cur.fetchall()
    return render_template("volunteer_dashboard.html", requests=data)

@app.route("/accept/<int:req_id>")
def accept(req_id):
    cur = get_db().cursor()
    cur.execute("""
    UPDATE requests
    SET status='Accepted', assigned_volunteer=?
    WHERE id=?
    """, (session["user_id"], req_id))
    cur.connection.commit()
    return redirect("/volunteer")

@app.route("/complete/<int:req_id>")
def complete(req_id):
    cur = get_db().cursor()
    cur.execute("UPDATE requests SET status='Completed' WHERE id=?", (req_id,))
    cur.connection.commit()
    return redirect("/volunteer")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
