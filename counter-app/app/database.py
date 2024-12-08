import sqlite3
import os

# Set the database path to the root directory
DB_NAME = '/counter.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE OR REPLACE TABLE IF NOT EXISTS counter (id INTEGER PRIMARY KEY, value INTEGER);")
    cursor.execute("INSERT OR IGNORE INTO counter (id, value) VALUES (1, 0);")
    conn.commit()
    conn.close()

def get_counter():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM counter WHERE id = 1;")
    value = cursor.fetchone()[0]
    conn.close()
    return value

def update_counter(delta):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE counter SET value = value + ? WHERE id = 1;", (delta,))
    conn.commit()
    conn.close()
