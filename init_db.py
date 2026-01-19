import sqlite3

con = sqlite3.connect("database.db")
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
    eta TEXT,
    rating INTEGER,
    feedback TEXT,
    rated INTEGER,
    timestamp TEXT,
    reasons TEXT
)
""")

con.commit()
con.close()

print("✅ Database & tables created successfully")
