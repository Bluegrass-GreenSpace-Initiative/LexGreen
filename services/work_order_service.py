from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from io import StringIO
import csv

from .database import Database
from .notify import SlackNotifier


class WorkOrderService:
    """Service to manage unified work orders for maintenance, damage, and volunteer tasks."""

    def __init__(self) -> None:
        self.db = Database()

    def ensure_tables(self) -> None:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS work_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL DEFAULT 'public',             -- public|internal
                    type TEXT NOT NULL,                                 -- damage|maintenance|volunteer|amenity
                    status TEXT NOT NULL DEFAULT 'open',               -- open|triaged|in_progress|blocked|resolved|cancelled
                    priority INTEGER NOT NULL DEFAULT 2,               -- 1..4
                    asset_type TEXT,                                   -- tree|amenity|area
                    tree_id INTEGER,
                    amenity_id INTEGER,
                    area_id INTEGER,
                    latitude REAL,
                    longitude REAL,
                    title TEXT,
                    description TEXT,
                    created_by_user_id TEXT,                           -- for public submissions
                    assigned_to TEXT,                                  -- staff email or name
                    resolution_note TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    resolved_at TEXT,
                    FOREIGN KEY(tree_id) REFERENCES trees(tree_id)
                )
                """
            )
            conn.commit()

    def create_from_damage_report(self, tree_id: int, user_id: str, severity: int, description: str) -> Tuple[bool, str, Optional[int]]:
        """Create a work order when a public damage report is submitted."""
        self.ensure_tables()
        priority = max(1, min(4, int(severity or 2)))
        title = 'Tree damage report'
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO work_orders (source, type, status, priority, asset_type, tree_id, title, description, created_by_user_id)
                VALUES ('public', 'damage', 'open', ?, 'tree', ?, ?, ?, ?)
                """,
                (priority, tree_id, title, description or '', user_id)
            )
            wid = cur.lastrowid
            conn.commit()
            wid = int(wid)
            # Slack notify if high priority
            try:
                if priority >= 3:
                    SlackNotifier().send(f":rotating_light: High-priority damage report → Work Order #{wid} (tree #{tree_id}) P{priority}: {description[:120]}")
            except Exception:
                pass
            return True, 'Work order created', wid

    def list(self, status: Optional[str] = None, type_: Optional[str] = None) -> List[Dict]:
        self.ensure_tables()
        where = []
        params: List = []
        if status:
            where.append('status = ?')
            params.append(status)
        if type_:
            where.append('type = ?')
            params.append(type_)
        where_sql = ('WHERE ' + ' AND '.join(where)) if where else ''
        q = f"SELECT id, source, type, status, priority, asset_type, tree_id, title, description, created_by_user_id, assigned_to, resolution_note, created_at, updated_at, resolved_at FROM work_orders {where_sql} ORDER BY created_at DESC"
        rows = self.db.execute_query(q, tuple(params))
        out: List[Dict] = []
        for r in rows:
            out.append({
                'id': r[0], 'source': r[1], 'type': r[2], 'status': r[3], 'priority': int(r[4] or 2),
                'asset_type': r[5], 'tree_id': r[6], 'title': r[7], 'description': r[8], 'created_by_user_id': r[9],
                'assigned_to': r[10], 'resolution_note': r[11], 'created_at': r[12], 'updated_at': r[13], 'resolved_at': r[14]
            })
        return out

    def get(self, work_order_id: int) -> Optional[Dict]:
        self.ensure_tables()
        rows = self.db.execute_query(
            "SELECT id, source, type, status, priority, asset_type, tree_id, title, description, created_by_user_id, assigned_to, resolution_note, created_at, updated_at, resolved_at FROM work_orders WHERE id = ?",
            (work_order_id,)
        )
        if not rows:
            return None
        r = rows[0]
        return {
            'id': r[0], 'source': r[1], 'type': r[2], 'status': r[3], 'priority': int(r[4] or 2), 'asset_type': r[5],
            'tree_id': r[6], 'title': r[7], 'description': r[8], 'created_by_user_id': r[9], 'assigned_to': r[10],
            'resolution_note': r[11], 'created_at': r[12], 'updated_at': r[13], 'resolved_at': r[14]
        }

    def update(self, work_order_id: int, *, status: Optional[str] = None, assigned_to: Optional[str] = None, resolution_note: Optional[str] = None, priority: Optional[int] = None) -> Tuple[bool, str]:
        self.ensure_tables()
        sets = []
        params: List = []
        if status:
            sets.append('status = ?')
            params.append(status)
            if status == 'resolved':
                sets.append("resolved_at = datetime('now')")
        if assigned_to is not None:
            sets.append('assigned_to = ?')
            params.append(assigned_to)
        if resolution_note is not None:
            sets.append('resolution_note = ?')
            params.append(resolution_note)
        if priority is not None:
            sets.append('priority = ?')
            params.append(max(1, min(4, int(priority))))
        if not sets:
            return True, 'No changes'
        sets.append("updated_at = datetime('now')")
        params.append(work_order_id)
        self.db.execute_write(f"UPDATE work_orders SET {', '.join(sets)} WHERE id = ?", tuple(params))
        return True, 'Updated'

    def create_from_volunteer(self, *, user_id: str, task: str, latitude: Optional[float], longitude: Optional[float], area_name: Optional[str] = None, note: str = '') -> Tuple[bool, str, Optional[int]]:
        """Create a work order representing a public volunteer task (e.g., remove invasive plants)."""
        self.ensure_tables()
        uid = (user_id or '').strip()
        if not uid:
            return False, 'Missing user id', None
        title = (task or 'Volunteer task').strip()
        desc_parts = []
        if area_name:
            desc_parts.append(f"Area: {area_name}")
        if note:
            desc_parts.append(note)
        desc = ' • '.join([p for p in desc_parts if p])
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                (
                    "INSERT INTO work_orders (source, type, status, priority, asset_type, latitude, longitude, title, description, created_by_user_id) "
                    "VALUES ('public', 'volunteer', 'open', 2, 'area', ?, ?, ?, ?, ?)"
                ),
                (latitude, longitude, title, desc, uid)
            )
            wid = int(cur.lastrowid)
            conn.commit()
            return True, 'Work order created', wid

    def export_csv(self, since_iso: Optional[str] = None) -> str:
        self.ensure_tables()
        where = ''
        params: List = []
        if since_iso:
            where = 'WHERE created_at >= ?'
            params.append(since_iso)
        rows = self.db.execute_query(
            f"SELECT id, source, type, status, priority, asset_type, tree_id, title, description, created_by_user_id, assigned_to, resolution_note, created_at, updated_at, resolved_at FROM work_orders {where} ORDER BY created_at DESC",
            tuple(params)
        )
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(['id', 'source', 'type', 'status', 'priority', 'asset_type', 'tree_id', 'title', 'description', 'created_by_user_id', 'assigned_to', 'resolution_note', 'created_at', 'updated_at', 'resolved_at'])
        for r in rows:
            w.writerow(r)
        return buf.getvalue()

    def list_for_user(self, user_id: str) -> List[Dict]:
        """List work orders created by a public user, joined with tree info when available."""
        self.ensure_tables()
        q = (
            "SELECT w.id, w.type, w.status, w.priority, w.asset_type, w.tree_id, w.title, w.description, w.created_at, w.updated_at, w.resolved_at, "
            "t.common_name, t.latin_name, t.latitude, t.longitude "
            "FROM work_orders w LEFT JOIN trees t ON t.tree_id = w.tree_id "
            "WHERE w.created_by_user_id = ? "
            "GROUP BY w.id "
            "ORDER BY w.created_at DESC"
        )
        rows = self.db.execute_query(q, (user_id,))
        out: List[Dict] = []
        for r in rows:
            out.append({
                'id': r[0], 'type': r[1], 'status': r[2], 'priority': int(r[3] or 2), 'asset_type': r[4], 'tree_id': r[5],
                'title': r[6], 'description': r[7], 'created_at': r[8], 'updated_at': r[9], 'resolved_at': r[10],
                'common_name': r[11], 'latin_name': r[12], 'latitude': r[13], 'longitude': r[14]
            })
        return out
