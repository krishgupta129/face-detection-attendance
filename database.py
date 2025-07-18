import sqlite3
import pickle
from datetime import datetime

DB_PATH = 'database/attendance.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            encoding BLOB NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            user_id TEXT,
            name TEXT,
            date TEXT,
            time TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user(user_id, name, phone, encoding):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
              (user_id, name, phone, pickle.dumps(encoding)))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, phone, encoding FROM users")
    rows = c.fetchall()
    users = []
    for uid, name, phone, enc in rows:
        users.append((uid, name, phone, pickle.loads(enc)))
    conn.close()
    return users

def mark_attendance(user_id, name):
    conn = get_connection()
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    c.execute("SELECT * FROM attendance WHERE user_id=? AND date=?", (user_id, date))
    if not c.fetchone():
        c.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)", (user_id, name, date, time))
    conn.commit()
    conn.close()

def get_attendance_records():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM attendance ORDER BY date DESC, time DESC")
    records = c.fetchall()
    conn.close()
    return records

def delete_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    c.execute("DELETE FROM attendance WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def update_user(user_id, name, phone):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET name = ?, phone = ? WHERE id = ?", (name, phone, user_id))
    conn.commit()
    conn.close()
