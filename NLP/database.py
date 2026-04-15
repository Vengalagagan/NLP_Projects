import sqlite3

conn = sqlite3.connect("feedback.db", check_same_thread=False)
c = conn.cursor()

def create_tables():
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student TEXT,
        faculty TEXT,
        course TEXT,
        feedback TEXT,
        sentiment TEXT,
        rating INTEGER
    )
    """)
    conn.commit()


def add_user(username, password, role):
    c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, role))
    conn.commit()


def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()


def save_feedback(student, faculty, course, feedback, sentiment, rating):
    c.execute("INSERT INTO feedback (student, faculty, course, feedback, sentiment, rating) VALUES (?, ?, ?, ?, ?, ?)",
              (student, faculty, course, feedback, sentiment, rating))
    conn.commit()


def get_teacher_feedback(faculty):
    c.execute("SELECT * FROM feedback WHERE faculty=?", (faculty,))
    return c.fetchall()


def get_all_feedback():
    c.execute("SELECT * FROM feedback")
    return c.fetchall()