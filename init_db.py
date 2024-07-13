import sqlite3

def initialize_db():
    try:
        conn = sqlite3.connect('diary.db')
        c = conn.cursor()

        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT UNIQUE,
                password TEXT
            )
        ''')

        # Create entries table
        c.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                entry TEXT,
                timestamp TEXT
            )
        ''')

        conn.commit()
        print("Database initialized successfully.")

    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    initialize_db()