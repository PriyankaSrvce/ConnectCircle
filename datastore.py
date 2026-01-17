import sqlite3

def get_db():
    return sqlite3.connect("connectcircle.db", check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS volunteers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        rating REAL DEFAULT 5.0
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        description TEXT,
        severity INTEGER,
        status TEXT,
        volunteer TEXT
    )""")

    db.commit()
