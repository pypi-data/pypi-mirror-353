import sqlite3

def init_db():
    conn = sqlite3.connect("easedb.sqlite")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS containers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            container_id TEXT NOT NULL,
            db_type TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_container_info(name, container_id, db_type):
    conn = sqlite3.connect("easedb.sqlite")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO containers (name, container_id, db_type) VALUES (?, ?, ?)", (name, container_id, db_type))
    conn.commit()
    conn.close()

def get_containers():
    conn = sqlite3.connect("easedb.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM containers")
    containers = cursor.fetchall()
    conn.close()
    return containers
