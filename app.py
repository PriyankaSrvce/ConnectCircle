from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os, heapq

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        location INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seeker TEXT,
        category TEXT,
        description TEXT,
        image TEXT,
        priority TEXT,
        status TEXT
    )
    """)

    db.commit()
    db.close()

init_db()

# ---------- EMERGENCY LOGIC ----------
URGENT_KEYWORDS = ["urgent", "pain", "fell", "help fast", "emergency"]

def classify_request(category, description, volunteers_nearby):
    if category in ["Medical", "Safety", "Mobility"]:
        return "Emergency"

    count = sum(1 for w in URGENT_KEYWORDS if w in description.lower())
    if count >= 2:
        return "Emergency"

    if not volunteers_nearby:
        return "Emergency"

    return "Normal"

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]

        db = get_db()
        db.execute("INSERT INTO users(name, role, location) VALUES(?,?,?)",
                   (name, role, 1))
        db.commit()
        db.close()

        if role == "Seeker":
            return redirect(url_for("seeker_home", name=name))
        else:
            return redirect(url_for("volunteer_home", name=name))

    return render_template("login.html")

@app.route("/seeker/<name>")
def seeker_home(name):
    return render_template("seeker_home.html", name=name)

@app.route("/create_request/<name>", methods=["GET", "POST"])
def create_request(name):
    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]

        image = None
        if "image" in request.files:
            file = request.files["image"]
            if file.filename:
                image = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(image)

        # Simulated volunteer graph availability
        volunteers_nearby = True

        priority = classify_request(category, description, volunteers_nearby)

        db = get_db()
        db.execute("""
        INSERT INTO requests(seeker, category, description, image, priority, status)
        VALUES(?,?,?,?,?,?)
        """, (name, category, description, image, priority, "Searching"))
        db.commit()
        db.close()

        return redirect(url_for("request_status", name=name))

    return render_template("create_request.html", name=name)

@app.route("/status/<name>")
def request_status(name):
    db = get_db()
    req = db.execute("""
    SELECT * FROM requests WHERE seeker=? ORDER BY id DESC LIMIT 1
    """, (name,)).fetchone()
    db.close()

    return render_template("request_status.html", req=req)

@app.route("/volunteer/<name>")
def volunteer_home(name):
    db = get_db()
    requests = db.execute("""
    SELECT * FROM requests WHERE status='Searching'
    ORDER BY CASE priority WHEN 'Emergency' THEN 1 ELSE 2 END
    """).fetchall()
    db.close()

    return render_template("volunteer_home.html", name=name, requests=requests)

if __name__ == "__main__":
    app.run(debug=True)
