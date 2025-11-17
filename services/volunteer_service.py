from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from .database import Database


class VolunteerService:
    """Manage volunteer requests (e.g., invasive plant removal)."""

    def __init__(self) -> None:
        self.db = Database()

    def ensure_tables(self) -> None:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS volunteer_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    task TEXT NOT NULL,
                    area_id INTEGER,
                    latitude REAL,
                    longitude REAL,
                    note TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    permit_valid_from TEXT,
                    permit_valid_to TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.commit()

    def create(self, *, user_id: str, task: str, area_id: Optional[int] = None, latitude: Optional[float] = None, longitude: Optional[float] = None, note: str = '') -> Tuple[bool, str, Optional[int]]:
        """Insert a volunteer request. Returns (ok, msg, request_id)."""
        self.ensure_tables()
        uid = (user_id or '').strip()
        if not uid:
            return False, 'Missing user id', None
        task = (task or '').strip() or 'volunteer task'
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                (
                    "INSERT INTO volunteer_requests (user_id, task, area_id, latitude, longitude, note, status) "
                    "VALUES (?, ?, ?, ?, ?, ?, 'pending')"
                ),
                (uid, task, area_id, latitude, longitude, note)
            )
            rid = int(cur.lastrowid)
            conn.commit()
            return True, 'Volunteer request submitted', rid

    def list(self, status: Optional[str] = None) -> List[Dict]:
        self.ensure_tables()
        if status:
            rows = self.db.execute_query(
                "SELECT id, user_id, task, area_id, latitude, longitude, note, status, permit_valid_from, permit_valid_to, created_at, updated_at FROM volunteer_requests WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
        else:
            rows = self.db.execute_query(
                "SELECT id, user_id, task, area_id, latitude, longitude, note, status, permit_valid_from, permit_valid_to, created_at, updated_at FROM volunteer_requests ORDER BY created_at DESC"
            )
        return [
            {
                'id': r[0], 'user_id': r[1], 'task': r[2], 'area_id': r[3], 'latitude': r[4], 'longitude': r[5],
                'note': r[6], 'status': r[7], 'permit_valid_from': r[8], 'permit_valid_to': r[9], 'created_at': r[10], 'updated_at': r[11]
            }
            for r in rows
        ]

    def update(self, request_id: int, *, status: Optional[str] = None, permit_valid_from: Optional[str] = None, permit_valid_to: Optional[str] = None) -> Tuple[bool, str]:
        self.ensure_tables()
        sets = []
        params: List = []  # type: ignore[name-defined]
        if status:
            sets.append('status = ?'); params.append(status)
        if permit_valid_from is not None:
            sets.append('permit_valid_from = ?'); params.append(permit_valid_from)
        if permit_valid_to is not None:
            sets.append('permit_valid_to = ?'); params.append(permit_valid_to)
        if not sets:
            return True, 'No changes'
        sets.append("updated_at = datetime('now')")
        params.append(request_id)
        self.db.execute_write(f"UPDATE volunteer_requests SET {', '.join(sets)} WHERE id = ?", tuple(params))
        return True, 'Volunteer request updated'

    def delete(self, request_id: int) -> Tuple[bool, str]:
        self.ensure_tables()
        rows = self.db.execute_query("SELECT id FROM volunteer_requests WHERE id = ?", (request_id,))
        if not rows:
            return False, 'Not found'
        self.db.execute_write("DELETE FROM volunteer_requests WHERE id = ?", (request_id,))
        return True, 'Deleted'
