import sqlite3
import json
import time
from config import DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            place TEXT NOT NULL,
            phone TEXT NOT NULL,
            mode TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL,
            score INTEGER DEFAULT -1,
            answers TEXT NOT NULL,
            status TEXT DEFAULT 'started'
        )
    """)
    conn.commit()
    conn.close()

def create_participant(name, age, place, phone, mode):
    conn = get_connection()
    cursor = conn.cursor()
    start_time = time.time()
    cursor.execute("""
        INSERT INTO participants (name, age, place, phone, mode, start_time, answers, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, place, phone, mode, start_time, json.dumps({}), "started"))
    conn.commit()
    participant_id = cursor.lastrowid
    conn.close()
    return participant_id

def update_answers(participant_id, answers_dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE participants
        SET answers = ?
        WHERE id = ?
    """, (json.dumps(answers_dict), participant_id))
    conn.commit()
    conn.close()

def submit_exam(participant_id, score, status):
    conn = get_connection()
    cursor = conn.cursor()
    end_time = time.time()
    cursor.execute("""
        UPDATE participants
        SET score = ?, end_time = ?, status = ?
        WHERE id = ?
    """, (score, end_time, status, participant_id))
    conn.commit()
    conn.close()

def get_participant(participant_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM participants WHERE id = ?", (participant_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_active_participant_by_phone(phone):
    conn = get_connection()
    cursor = conn.cursor()
    # Find the latest started record for this phone in the last 100 minutes
    min_start_time = time.time() - 100 * 60
    cursor.execute("""
        SELECT * FROM participants
        WHERE phone = ? AND status = 'started' AND start_time > ?
        ORDER BY start_time DESC LIMIT 1
    """, (phone, min_start_time))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_all_results():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM participants ORDER BY start_time DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def reset_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS participants")
    conn.commit()
    conn.close()
    init_db()
