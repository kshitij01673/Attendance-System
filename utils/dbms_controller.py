#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sqlite3
from datetime import datetime



# In[ ]:


# Database file name
DB_NAME = "utils//attendance.db"

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect(DB_NAME)

# Create a cursor object
cursor = conn.cursor()

# Create tables if they do not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    hash TEXT UNIQUE NOT NULL,
    created_at NOT NULL
)
""")

cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    S_no INTEGER PRIMARY KEY AUTOINCREMENT,
    id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT,
    presence BOOLEAN DEFAULT 0,
    ab_approved BOOLEAN,
    device_id TEXT NOT NULL,
    FOREIGN KEY (id) REFERENCES users(id)
)
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS device (
    S_no INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT UNIQUE NOT NULL,
    location TEXT
)
''')

# Save changes
conn.commit()

print("Database connected successfully.")
print("Tables created (if they didn't already exist).")

# Close the connection
conn.close()


# In[ ]:


#note: add a table for devices

'''Daily Initialization

Every morning:

All students
↓
Status = Absent

Then when a student scans:

Absent → Present

This is also a good approach because:

You don't need an extra "mark absences" step.
The IoT device only changes a student's status from Absent to Present.'''


# In[ ]:


def initialize_attendance(conn, device_id="SYSTEM"):
    """
    Creates today's attendance records for every student.
    """

    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    # Prevent duplicate initialization
    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ?",
        (today,)
    )

    if cursor.fetchone()[0] > 0:
        print("Today's attendance already initialized.")
        return

    cursor.execute("SELECT id, name FROM users")
    students = cursor.fetchall()

    for id, name in students:
        cursor.execute("""
            INSERT INTO attendance
            (id, date, time, presence, device_id)
            VALUES (?, ?, NULL, 0, ?)
        """, (id, today, device_id))

    conn.commit()


# In[ ]:


def mark_presence(conn, id, device_id):
    """
    Marks a student present for today's attendance.
    """

    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
        UPDATE attendance
        SET presence = 1,
            time = ?,
            device_id = ?
        WHERE id = ?
          AND date = ?
    """, (current_time, device_id, id, today))

    conn.commit()

    if cursor.rowcount == 0:
        print(f"Attendance record not initialized for today for {id}")
        return False

    return True


# In[ ]:


def verify_user_hash(conn, user_hash):
    """
    Returns True if the hash exists in the users table, otherwise False.
    """
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM users WHERE hash = ? LIMIT 1",
        (user_hash,)
    )

    return cursor.fetchone() is not None


# In[1]:


# In[ ]:


def device_exists(conn, device_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM device WHERE id = ? LIMIT 1",
        (device_id,)
    )
    return cursor.fetchone() is not None


# In[ ]:


def user_exists(conn, user_id, name, user_hash):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1
        FROM users
        WHERE id = ? AND name = ? AND hash = ?
        LIMIT 1
    """, (user_id, name, user_hash))

    return cursor.fetchone() is not None

