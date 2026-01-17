import sqlite3

def get_db():
    conn = sqlite3.connect("connectcircle.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        role TEXT
    )
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY,
        category TEXT,
        description TEXT,
        priority INTEGER,
        status TEXT,
        volunteer_id INTEGER
    )
    """)
    db.commit()
