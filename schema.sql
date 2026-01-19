DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS requests;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
);

CREATE TABLE requests (
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
);
