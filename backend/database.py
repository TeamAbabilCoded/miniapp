import sqlite3
from config import DB_PATH

def connect_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Log klik user
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS click_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        task_id INTEGER,
        timestamp TEXT,
        ip TEXT,
        user_agent TEXT,
        UNIQUE(user_id, task_id)
    )
    """)

    # Daftar tugas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        long_url TEXT,
        short_url TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def insert_task(name, long_url, short_url):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (name, long_url, short_url) VALUES (?, ?, ?)", (name, long_url, short_url))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, short_url FROM tasks")
    tasks = cur.fetchall()
    conn.close()
    return tasks
