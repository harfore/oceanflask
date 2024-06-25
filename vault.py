import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import datetime
from functools import partial


def ensure_unique_usernames():
    conn = sqlite3.connect('diary.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users_new (
            username TEXT UNIQUE,
            password TEXT
        )
    ''') # only create the account if the username isn't already in the database

    c.execute('INSERT OR IGNORE INTO users_new (username, password) SELECT username, password FROM users')

    c.execute('DROP TABLE users')

    c.execute('ALTER TABLE users_new RENAME TO users')

    conn.commit()
    conn.close()

ensure_unique_usernames()

conn = sqlite3.connect('diary.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS entries (username TEXT, entry TEXT, timestamp TEXT)''')
conn.commit()

c.execute("PRAGMA table_info(entries)")
columns = [info[1] for info in c.fetchall()]
if 'timestamp' not in columns:
    c.execute('ALTER TABLE entries ADD COLUMN timestamp TEXT')
    conn.commit()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user():
    username = entry_username.get()
    password = entry_password.get()
    
    if not username or not password:
        messagebox.showerror("Error", "Username and Password cannot be empty")
        return
    
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    if c.fetchone():
        messagebox.showerror("Error", "Username already exists")
        return
    
    hashed_password = hash_password(password)

    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    messagebox.showinfo("Success", "Registration Successful")


def login_user():
    username = entry_username.get()
    password = entry_password.get()
    
    if not username or not password:
        messagebox.showerror("Error", "Username and Password cannot be empty")
        return
    
    hashed_password = hash_password(password)
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hashed_password))
    if c.fetchone():
        messagebox.showinfo("Success", "Login Successful")
        diary_screen(username)
    else:
        messagebox.showerror("Error", "Invalid Credentials")


def diary_screen(username):
    root.withdraw()
    diary = tk.Toplevel(root)
    diary.title("Diary Entries")

    def add_entry():
        entry = entry_text.get("1.0", tk.END)
        timestamp = datetime.datetime.now().strftime("%Y %m %d %H:%M:%S")
        c.execute('INSERT INTO entries (username, entry, timestamp) VALUES (?, ?, ?)', (username, entry, timestamp))
        conn.commit()
        messagebox.showinfo("Success", "Entry Added")
        entry_text.delete("1.0", tk.END)

    def view_entries():
        c.execute('SELECT rowid, entry, timestamp FROM entries WHERE username=?', (username,))
        entries = c.fetchall()
    
        if not entries:
            messagebox.showinfo("No Entries", "No entries found.")
            return
    
        entries_window = tk.Toplevel(diary)
        entries_window.title("Previous Entries")
    
        for rowid, entry, timestamp in entries:
            entry_frame = tk.Frame(entries_window)
            entry_frame.pack(fill='x')
        
            entry_label = tk.Label(entry_frame, text=f"{timestamp}: {entry}", anchor='w')
            entry_label.pack(side='left', fill='x', expand=True)
        
            delete_button = tk.Button(entry_frame, text="Delete", command=partial(delete_entry, rowid, entries_window))
            delete_button.pack(side='right')
            
    def delete_entry(rowid, entries_window):
        c.execute('DELETE FROM entries WHERE rowid=?', (rowid,))
        conn.commit()
        messagebox.showinfo("Success", "Entry Deleted")
        entries_window.destroy()
        view_entries()


    entry_text = tk.Text(diary, height=10, width=50)
    entry_text.pack()
    button_add = tk.Button(diary, text="Add Entry", command=add_entry)
    button_add.pack()
    button_view = tk.Button(diary, text="View Previous Entries", command=view_entries)
    button_view.pack()
    button_logout = tk.Button(diary, text="Logout", command=lambda: logout(diary))
    button_logout.pack()



def logout(diary):
    diary.destroy()
    root.deiconify()

root = tk.Tk()
root.title("Diary Login")

label_username = tk.Label(root, text="Username")
label_username.pack()
entry_username = tk.Entry(root)
entry_username.pack()

label_password = tk.Label(root, text="Password")
label_password.pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

button_register = tk.Button(root, text="Register", command=register_user)
button_register.pack()
button_login = tk.Button(root, text="Login", command=login_user)
button_login.pack()

root.mainloop()