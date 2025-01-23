from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import datetime
from datetime import datetime
current_timestamp = datetime.now()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

conn = sqlite3.connect('diary.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, entry TEXT, timestamp TEXT)''')
conn.commit()

# Add 'timestamp' column if it doesn't exist in 'entries' table
c.execute("PRAGMA table_info(entries)")
columns = [info[1] for info in c.fetchall()]
if 'timestamp' not in columns:
    c.execute('ALTER TABLE entries ADD COLUMN timestamp TEXT')
    conn.commit()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    conn = sqlite3.connect('diary.db')
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

def get_user_from_db(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = c.fetchone()
    conn.close()
    return user

@app.template_filter('strftime')
def format_datetime(value, format='%B %d, %Y'):
    """Format a datetime object using strftime."""
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

@app.route('/')
def index():
    entries = [
        "Discovery, released in 2001, is the second album released by electronic French duo Daft Punk.",
        "Discovery, released in 2001, is the second album released by electronic French duo Daft Punk.",
        "10 months sober today.",
        "Discovery, released in 2001, is the second album released by electronic French duo Daft Punk."
    ]
    return render_template('index.html', entries=entries)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Username and Password cannot be empty', 'error')
            return redirect(url_for('register'))
        
        hashed_password = hash_password(password)

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        flash('Registration Successful', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username and Password cannot be empty', 'error')
            return redirect(url_for('login'))

        hashed_password = hash_password(password)
        user = get_user_from_db(username, hashed_password)

        if user:
            session['username'] = username
            flash('Login Successful', 'success')
            return redirect(url_for('account_menu'))
        else:
            flash('Invalid Credentials', 'error')

    return render_template('login.html')

@app.route('/account_menu')
def account_menu():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('account_menu.html')

@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        try:
            entry = request.form['entry']
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('INSERT INTO entries (username, entry, timestamp) VALUES (?, ?, ?)', (username, entry, timestamp))
            conn.commit()
            flash('Entry Added', 'success')
        except Exception as e:
            flash('An error occurred while adding your entry.', 'error')

    c.execute('SELECT id, entry, timestamp FROM entries WHERE username=?', (username,))
    entries = [
        {
            'id': entry['id'],
            'entry': entry['entry'],
            'timestamp': datetime.strptime(entry['timestamp'], "%Y-%m-%d %H:%M:%S")
        }
        for entry in c.fetchall()
    ]
    conn.close()

    return render_template('diary.html', entries=entries, current_timestamp=current_timestamp)

@app.route('/view_entry/<int:entry_id>', methods=['GET'])
def view_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        'SELECT id, entry, timestamp FROM entries WHERE id = ? AND username = ?',
        (entry_id, username)
    )
    entry = c.fetchone()
    conn.close()

    if not entry:
        return redirect(url_for('diary'))

    return render_template('view_entry.html', entry=entry)


@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM entries WHERE id=?', (entry_id,))
    conn.commit()
    conn.close()

    flash('Entry Deleted', 'success')
    return redirect(url_for('diary'))

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if request.method == 'POST':
        entry_content = request.form.get('entry')  # Get the entry content from the form
        if not entry_content.strip():
            flash("Entry cannot be empty", "warning")
            return redirect(url_for('new_entry'))

        # Save the entry to the database
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            'INSERT INTO entries (username, entry, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)',
            (username, entry_content)
        )
        conn.commit()
        conn.close()

        flash("New entry created!", "success")
        return redirect(url_for('diary'))  # Redirect to the diary page

    # If GET request, show the new entry form
    return render_template('new_entry.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)