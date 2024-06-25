# init_db.py
import sqlite3

def initialize_db():
    conn = sqlite3.connect('diary.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            username TEXT,
            entry TEXT,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_db()