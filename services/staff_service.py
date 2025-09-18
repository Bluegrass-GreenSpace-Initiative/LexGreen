from __future__ import annotations

from typing import Optional, Tuple
from .database import Database
from werkzeug.security import generate_password_hash, check_password_hash


class StaffService:
    """Service for managing internal staff users for the admin portal."""

    def __init__(self) -> None:
        self.db = Database()

    def ensure_tables(self) -> None:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS staff_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    role TEXT NOT NULL DEFAULT 'staff',
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    last_login_at TEXT
                )
                """
            )
            conn.commit()

    def create_staff(self, email: str, password: str, name: Optional[str] = None, role: str = 'staff') -> Tuple[bool, str, Optional[int]]:
        self.ensure_tables()
        email = (email or '').strip().lower()
        if not email or not password:
            return False, 'Email and password are required', None
        pw_hash = generate_password_hash(password)
        try:
            with self.db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO staff_users (email, name, role, password_hash) VALUES (?, ?, ?, ?)",
                    (email, name, role, pw_hash)
                )
                sid = cur.lastrowid
                conn.commit()
                return True, 'Staff user created', int(sid)
        except Exception as e:
            return False, f'Failed to create staff user: {e}', None

    def verify_login(self, email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        self.ensure_tables()
        email = (email or '').strip().lower()
        if not email or not password:
            return False, 'Missing credentials', None
        rows = self.db.execute_query("SELECT id, email, name, role, password_hash FROM staff_users WHERE email = ?", (email,))
        if not rows:
            return False, 'Invalid email or password', None
        rid, remail, rname, rrole, rhash = rows[0]
        if not check_password_hash(rhash, password):
            return False, 'Invalid email or password', None
        # Update last_login_at
        self.db.execute_write("UPDATE staff_users SET last_login_at = datetime('now') WHERE id = ?", (rid,))
        return True, 'Login successful', {'id': rid, 'email': remail, 'name': rname, 'role': rrole}

