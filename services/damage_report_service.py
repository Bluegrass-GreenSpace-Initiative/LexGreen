from __future__ import annotations

from typing import Optional, Dict, List, Tuple
from io import StringIO
import csv
from .database import Database


class DamageReportService:
    """Service for recording and exporting tree damage reports.

    Schema (tree_damage_reports):
      id INTEGER PK
      tree_id INTEGER NOT NULL
      user_id TEXT NOT NULL
      issue_type TEXT NOT NULL
      severity INTEGER NOT NULL DEFAULT 1  -- 1..4
      description TEXT NOT NULL DEFAULT ''
      reported_at TEXT NOT NULL DEFAULT (datetime('now'))
    """

    def __init__(self):
        self.db = Database()

    def ensure_tables(self) -> None:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tree_damage_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tree_id INTEGER NOT NULL,
                    user_id TEXT NOT NULL,
                    issue_type TEXT NOT NULL,
                    severity INTEGER NOT NULL DEFAULT 1,
                    description TEXT NOT NULL DEFAULT '',
                    reported_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY(tree_id) REFERENCES trees(tree_id)
                )
                """
            )
            # Best-effort dedupe for accidental duplicate inserts (same second)
            try:
                cur.execute(
                    "DELETE FROM tree_damage_reports WHERE id NOT IN ("
                    "  SELECT MIN(id) FROM tree_damage_reports "
                    "  GROUP BY tree_id, user_id, issue_type, severity, description, reported_at"
                    ")"
                )
            except Exception:
                pass
            conn.commit()

    def add_report(self, tree_id: int, user_id: str, issue_type: str, severity: int, description: str) -> Tuple[bool, str, Optional[int]]:
        """Insert a report; debounce duplicates submitted within ~2 seconds with identical fields."""
        self.ensure_tables()
        issue_type = (issue_type or '').strip() or 'unspecified'
        description = (description or '').strip()
        try:
            severity = int(severity)
        except Exception:
            severity = 1
        severity = max(1, min(4, severity))
        if not user_id:
            return False, 'Missing user id', None

        with self.db.get_connection() as conn:
            cur = conn.cursor()
            # Debounce: if an identical report exists very recently, return it instead of inserting
            cur.execute(
                "SELECT id FROM tree_damage_reports "
                "WHERE tree_id = ? AND user_id = ? AND issue_type = ? AND severity = ? AND description = ? "
                "AND reported_at >= datetime('now','-2 seconds') "
                "ORDER BY reported_at DESC LIMIT 1",
                (tree_id, user_id, issue_type, severity, description)
            )
            row = cur.fetchone()
            if row:
                return True, 'Report submitted', int(row[0])

            cur.execute(
                "INSERT INTO tree_damage_reports (tree_id, user_id, issue_type, severity, description) "
                "VALUES (?, ?, ?, ?, ?)",
                (tree_id, user_id, issue_type, severity, description)
            )
            rid = cur.lastrowid
            conn.commit()
            return True, 'Report submitted', int(rid)

    def list_for_tree(self, tree_id: int) -> List[Dict]:
        self.ensure_tables()
        q = "SELECT id, tree_id, user_id, issue_type, severity, description, reported_at FROM tree_damage_reports WHERE tree_id = ? ORDER BY reported_at DESC"
        rows = self.db.execute_query(q, (tree_id,))
        return [
            {
                'id': r[0], 'tree_id': r[1], 'user_id': r[2],
                'issue_type': r[3], 'severity': int(r[4] or 1),
                'description': r[5], 'reported_at': r[6]
            }
            for r in rows
        ]

    def export_csv(self, since_iso: Optional[str] = None) -> str:
        """Return CSV string for all reports (optionally since a date), joined with tree info."""
        self.ensure_tables()
        where = ""
        params: List = []
        if since_iso:
            where = "WHERE r.reported_at >= ?"
            params.append(since_iso)
        q = (
            "SELECT r.id, r.tree_id, r.user_id, r.issue_type, r.severity, r.description, r.reported_at, "
            "t.common_name, t.latin_name, t.latitude, t.longitude, t.dbh "
            "FROM tree_damage_reports r LEFT JOIN trees t ON t.tree_id = r.tree_id "
            f"{where} ORDER BY r.reported_at DESC"
        )
        rows = self.db.execute_query(q, tuple(params))
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow([
            'report_id', 'tree_id', 'user_id', 'issue_type', 'severity', 'description', 'reported_at',
            'tree_common_name', 'tree_latin_name', 'tree_latitude', 'tree_longitude', 'tree_dbh_cm'
        ])
        for r in rows:
            w.writerow(r)
        return buf.getvalue()

    def list_for_user(self, user_id: str) -> List[Dict]:
        """List all reports submitted by a user, newest first, joined with tree info."""
        self.ensure_tables()
        q = (
            "SELECT r.id, r.tree_id, r.issue_type, r.severity, r.description, r.reported_at, "
            "t.common_name, t.latin_name, t.latitude, t.longitude "
            "FROM tree_damage_reports r JOIN trees t ON t.tree_id = r.tree_id "
            "WHERE r.user_id = ? ORDER BY r.reported_at DESC"
        )
        rows = self.db.execute_query(q, (user_id,))
        out: List[Dict] = []
        for r in rows:
            out.append({
                'report_id': r[0],
                'tree_id': r[1],
                'issue_type': r[2],
                'severity': int(r[3] or 1),
                'description': r[4],
                'reported_at': r[5],
                'common_name': r[6],
                'latin_name': r[7],
                'latitude': r[8],
                'longitude': r[9],
            })
        return out

    def delete_report(self, report_id: int, user_id: str) -> Tuple[bool, str]:
        """Delete a report if it belongs to the given user."""
        self.ensure_tables()
        rows = self.db.execute_query(
            "SELECT id FROM tree_damage_reports WHERE id = ? AND user_id = ?",
            (report_id, user_id)
        )
        if not rows:
            return False, 'Report not found'
        self.db.execute_write("DELETE FROM tree_damage_reports WHERE id = ?", (report_id,))
        return True, 'Report deleted'
