from flask import Flask, render_template, request, redirect, session
import sqlite3, heapq, re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "connectcircle"

# ---------- DATABASE ----------
def db():
    return sqlite3.connect("database.db")

# ---------- AUTH ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = db()
        cur = con.cursor()
        cur.execute(
            "SELECT username, role FROM users WHERE username=? AND password=?",
            (u, p)
        )
        user = cur.fetchone()
        con.close()

        if user:
            session["user"] = user[0]
            session["role"] = user[1]
            return redirect("/seeker" if user[1] == "Seeker" else "/volunteer")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        con = db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?)",
            (request.form["username"],
             request.form["password"],
             request.form["role"])
        )
        con.commit()
        con.close()
        return redirect("/")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- EMERGENCY CLASSIFIER ----------
def classify(category, description):
    score = 0
    reasons = []

    if category in ["Medical", "Safety", "Mobility"]:
        score += 1
        reasons.append("Emergency Category")

    keywords = [
        "urgent", "emergency", "accident", "bleeding",
        "severe pain", "critical", "injured", "fell down",
        "cant breathe", "chest pain", "stroke"
    ]

    hits = sum(
        1 for k in keywords
        if re.search(rf"\b{k}\b", description.lower())
    )

    if hits >= 2:
        score += 1
        reasons.append(f"{hits} Urgent Keywords")

    con = db()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE role='Volunteer'")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM requests WHERE status='Accepted'")
    busy = cur.fetchone()[0]
    con.close()

    if total - busy <= 0:
        score += 1
        reasons.append("No Volunteers Available")

    return score > 0, ", ".join(reasons)

# ---------- SEEKER ----------
@app.route("/seeker", methods=["GET", "POST"])
def seeker():
    if session.get("role") != "Seeker":
        return redirect("/")

    con = db()
    cur = con.cursor()

    if request.method == "POST":
        emergency, reasons = classify(
            request.form["category"],
            request.form["description"]
        )

        cur.execute("""
            INSERT INTO requests VALUES
            (NULL,?,?,?,?,?,'Pending',NULL,NULL,NULL,NULL,NULL,0,?,?)
        """, (
            session["user"],
            request.form["category"],
            request.form["description"],
            request.form["location"],
            1 if emergency else 0,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            reasons
        ))
        con.commit()

    cur.execute(
        "SELECT * FROM requests WHERE seeker=?",
        (session["user"],)
    )
    data = cur.fetchall()
    con.close()

    return render_template("seeker.html", requests=data)


@app.route("/rate", methods=["POST"])
def rate():
    con = db()
    cur = con.cursor()

    cur.execute("""
        UPDATE requests
        SET rating=?, feedback=?, rated=1
        WHERE id=? AND seeker=?
    """, (
        request.form["rating"],
        request.form["feedback"],
        request.form["id"],
        session["user"]
    ))

    con.commit()
    con.close()
    return redirect("/seeker")

# ---------- VOLUNTEER ----------
@app.route("/volunteer", methods=["GET", "POST"])
def volunteer():
    if session.get("role") != "Volunteer":
        return redirect("/")

    con = db()
    cur = con.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "accept":
            cur.execute("""
                UPDATE requests
                SET status='Accepted',
                    volunteer=?,
                    phone=?,
                    eta=?
                WHERE id=?
            """, (
                session["user"],
                request.form["phone"],
                request.form["eta"],
                request.form["id"]
            ))

        elif action == "complete":
            cur.execute("""
                UPDATE requests
                SET status='Completed'
                WHERE id=? AND volunteer=?
            """, (
                request.form["id"],
                session["user"]
            ))

        con.commit()

    # Pending requests (Priority Queue)
    cur.execute("SELECT * FROM requests WHERE status='Pending'")
    pending_raw = cur.fetchall()

    pq = []
    for r in pending_raw:
        heapq.heappush(pq, (-r[5], r))  # priority DESC

    pending = [heapq.heappop(pq)[1] for _ in range(len(pq))]

    # Accepted / Completed by this volunteer
    cur.execute(
        "SELECT * FROM requests WHERE volunteer=?",
        (session["user"],)
    )
    mine = cur.fetchall()

    con.close()

    return render_template(
        "volunteer.html",
        pending=pending,
        mine=mine
    )

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
