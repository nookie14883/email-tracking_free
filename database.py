import sqlite3

def init_db():
    conn = sqlite3.connect('visits.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            ip TEXT,
            user_agent TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS counter (
            date TEXT PRIMARY KEY,
            count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()
