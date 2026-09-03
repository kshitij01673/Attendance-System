#!/usr/bin/env python
# coding: utf-8

# In[1]:


### import sqlite3
import secrets
import string
import os
import sqlite3
from datetime import datetime
from utils import qrgen as qg


DB_FILE = "utils/attendance.db"


# ============================================================
# SCREEN
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress Enter to continue...")


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS device (
                S_no INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT UNIQUE NOT NULL,
                location TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hash TEXT UNIQUE NOT NULL,
                created_at NOT NULL
            )
        """)


# ============================================================
# DEVICE MANAGEMENT
# ============================================================

def generate_device_id():
    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "".join(
            secrets.choice(alphabet)
            for _ in range(4)
        )

        device_id = f"devf0{code}"

        with get_connection() as conn:
            exists = conn.execute(
                "SELECT 1 FROM device WHERE id = ?",
                (device_id,)
            ).fetchone()

        if not exists:
            return device_id


def add_device():
    clear_screen()

    print("=" * 60)
    print("ADD DEVICE")
    print("=" * 60)

    location = input("Enter device location: ").strip()

    if not location:
        print("\n[!] Location cannot be empty.")
        pause()
        return

    device_id = generate_device_id()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO device (id, location)
            VALUES (?, ?)
            """,
            (device_id, location)
        )

    print("\n" + "=" * 45)
    print("DEVICE ADDED SUCCESSFULLY")
    print("=" * 45)
    print(f"Device ID : {device_id}")
    print(f"Location  : {location}")
    print("=" * 45)

    pause()


def view_devices():
    clear_screen()

    print("=" * 65)
    print("REGISTERED DEVICES")
    print("=" * 65)

    with get_connection() as conn:
        devices = conn.execute(
            """
            SELECT S_no, id, location
            FROM device
            ORDER BY S_no
            """
        ).fetchall()

    if not devices:
        print("No devices registered.")
        print("=" * 65)
        pause()
        return

    print(f"{'S.No.':<8}{'Device ID':<20}{'Location'}")
    print("-" * 65)

    for device in devices:
        print(
            f"{device['S_no']:<8}"
            f"{device['id']:<20}"
            f"{device['location'] or '-'}"
        )

    print("=" * 65)
    print(f"Total devices: {len(devices)}")

    pause()



def delete_device():
    clear_screen()

    print("=" * 70)
    print("DELETE DEVICE")
    print("=" * 70)

    # Show all registered devices first
    with get_connection() as conn:
        devices = conn.execute(
            """
            SELECT S_no, id, location
            FROM device
            ORDER BY S_no
            """
        ).fetchall()

    if not devices:
        print("\nNo devices registered.")
        pause()
        return

    print(f"{'S.No.':<8}{'Device ID':<20}{'Location'}")
    print("-" * 70)

    for device in devices:
        print(
            f"{device['S_no']:<8}"
            f"{device['id']:<20}"
            f"{device['location'] or '-'}"
        )

    print("-" * 70)

    # Ask for device ID after displaying devices
    device_id = input("\nEnter Device ID to delete: ").strip()

    if not device_id:
        print("\n[!] Device ID cannot be empty.")
        pause()
        return

    with get_connection() as conn:

        device = conn.execute(
            """
            SELECT S_no, id, location
            FROM device
            WHERE id = ?
            """,
            (device_id,)
        ).fetchone()

        if device is None:
            print(f"\n[!] Device '{device_id}' was not found.")
            pause()
            return

        print("\nDevice selected:")
        print(f"  S.No.    : {device['S_no']}")
        print(f"  ID       : {device['id']}")
        print(f"  Location : {device['location'] or '-'}")

        confirmation = input(
            "\nDelete this device? [y/N]: "
        ).strip().lower()

        if confirmation != "y":
            print("\n[-] Deletion cancelled.")
            pause()
            return

        conn.execute(
            "DELETE FROM device WHERE id = ?",
            (device_id,)
        )

    print(f"\n[+] Device '{device_id}' deleted successfully.")

    pause()



def device_manager():
    while True:
        clear_screen()

        print("=" * 60)
        print("DEVICE MANAGEMENT")
        print("=" * 60)
        print("  1. Add Device")
        print("  2. View Devices")
        print("  3. Delete Device")
        print("  4. Back to Main Menu")
        print("=" * 60)

        choice = input("Select an option [1-4]: ").strip()

        if choice == "1":
            add_device()

        elif choice == "2":
            view_devices()

        elif choice == "3":
            delete_device()

        elif choice == "4":
            break

        else:
            print("\n[!] Invalid option. Please select 1-4.")
            pause()


# ============================================================
# USER MANAGEMENT
# ============================================================

def generate_user_hash():
    alphabet = string.ascii_letters + string.digits

    while True:
        random_code = "".join(
            secrets.choice(alphabet)
            for _ in range(20)
        )

        user_hash = f"userf0{random_code}"

        with get_connection() as conn:
            exists = conn.execute(
                "SELECT 1 FROM users WHERE hash = ?",
                (user_hash,)
            ).fetchone()

        if not exists:
            return user_hash



def add_user():
    clear_screen()

    print("=" * 60)
    print("ADD USER")
    print("=" * 60)

    name = input("Name: ").strip()

    if not name:
        print("\n[!] Name cannot be empty.")
        pause()
        return

    user_hash = generate_user_hash()
    created_at = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (name, hash, created_at)
            VALUES (?, ?, ?)
            """,
            (name, user_hash, created_at)
        )

        # Get the automatically assigned user ID
        user_id = cursor.lastrowid

    qg.generate_qr({"Name": name, "id": str(user_id), "auth_code":str(user_hash) })
    print("\n" + "=" * 60)
    print("USER ADDED SUCCESSFULLY")
    print("=" * 60)
    print(f"User ID : {user_id}")
    print(f"Name    : {name}")
    print(f"Hash    : {user_hash}")
    print(f"Created : {created_at}")
    print("=" * 60)

    pause()


def view_users():
    clear_screen()

    print("=" * 90)
    print("USERS")
    print("=" * 90)

    with get_connection() as conn:
        users = conn.execute(
            """
            SELECT id, name, hash, created_at
            FROM users
            ORDER BY id
            """
        ).fetchall()

    if not users:
        print("No users found.")
        print("=" * 90)
        pause()
        return

    print(
        f"{'ID':<5} "
        f"{'NAME':<20} "
        f"{'HASH':<30} "
        f"{'CREATED AT':<20}"
    )

    print("-" * 90)

    for user in users:
        print(
            f"{user['id']:<5} "
            f"{user['name'][:19]:<20} "
            f"{user['hash']:<30} "
            f"{user['created_at']:<20}"
        )

    print("-" * 90)
    print(f"Total users: {len(users)}")

    pause()


def delete_user():
    clear_screen()

    print("=" * 60)
    print("DELETE USER")
    print("=" * 60)

    user_id = input("Enter user ID: ").strip()

    if not user_id.isdigit():
        print("\n[!] Invalid ID.")
        pause()
        return

    user_id = int(user_id)

    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT id, name, hash
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        if not user:
            print("\n[!] No user found with that ID.")
            pause()
            return

        print("\nUser found:")
        print(f"  ID   : {user['id']}")
        print(f"  Name : {user['name']}")
        print(f"  Hash : {user['hash']}")

        confirmation = input(
            "\nDelete this user? [y/N]: "
        ).strip().lower()

        if confirmation != "y":
            print("\n[-] Deletion cancelled.")
            pause()
            return

        conn.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

    print("\n[+] User deleted successfully.")

    pause()


def user_manager():
    while True:
        clear_screen()

        print("=" * 60)
        print("USER MANAGEMENT")
        print("=" * 60)
        print("  1. Add User")
        print("  2. View Users")
        print("  3. Delete User")
        print("  4. Back to Main Menu")
        print("=" * 60)

        choice = input("Select an option [1-4]: ").strip()

        if choice == "1":
            add_user()

        elif choice == "2":
            view_users()

        elif choice == "3":
            delete_user()

        elif choice == "4":
            break

        else:
            print("\n[!] Invalid option. Please select 1-4.")
            pause()


# ============================================================
# MAIN MENU
# ============================================================

def main():
    initialize_database()

    while True:
        clear_screen()

        print("=" * 60)
        print("             ATTENDANCE DATABASE MANAGER")
        print("=" * 60)
        print("  1. Device Management")
        print("  2. User Management")
        print("  3. Exit")
        print("=" * 60)

        choice = input("Select an option [1-3]: ").strip()

        if choice == "1":
            device_manager()

        elif choice == "2":
            user_manager()

        elif choice == "3":
            clear_screen()
            print("Goodbye.")
            break

        else:
            print("\n[!] Invalid option. Please select 1-3.")
            pause()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()



# In[ ]:




