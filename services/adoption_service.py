from __future__ import annotations

from typing import Optional, Dict, Tuple
from .database import Database


class AdoptionService:
    """Lightweight persistence for per-tree adoption info.

    Schema (tree_adoptions):
      id INTEGER PK
      tree_id INTEGER NOT NULL
      user_id TEXT NOT NULL
      adopter_name TEXT NOT NULL DEFAULT ''
      adopted_at TEXT NOT NULL (ISO datetime)
      health INTEGER NOT NULL DEFAULT 0  -- 0..4 dots
    Note: for legacy installs without user_id column, we add it if missing.
    """

    def __init__(self):
        self.db = Database()

    def ensure_tables(self) -> None:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tree_adoptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tree_id INTEGER NOT NULL,
                    user_id TEXT NOT NULL,
                    adopter_name TEXT NOT NULL DEFAULT '',
                    adopted_at TEXT NOT NULL DEFAULT (datetime('now')),
                    health INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(tree_id) REFERENCES trees(tree_id)
                )
                """
            )
            # Best-effort migration: ensure user_id column exists
            cur.execute("PRAGMA table_info(tree_adoptions)")
            cols = [r[1] for r in cur.fetchall()]
            if 'user_id' not in cols:
                # Rebuild table to remove any legacy UNIQUE(tree_id) constraint and add user_id column
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tree_adoptions_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tree_id INTEGER NOT NULL,
                        user_id TEXT NOT NULL,
                        adopter_name TEXT NOT NULL DEFAULT '',
                        adopted_at TEXT NOT NULL DEFAULT (datetime('now')),
                        health INTEGER NOT NULL DEFAULT 0,
                        FOREIGN KEY(tree_id) REFERENCES trees(tree_id)
                    )
                    """
                )
                # Copy legacy rows with default user_id 'legacy'
                cur.execute(
                    "INSERT INTO tree_adoptions_new (tree_id, user_id, adopter_name, adopted_at, health) "
                    "SELECT tree_id, 'legacy' as user_id, adopter_name, adopted_at, health FROM tree_adoptions"
                )
                cur.execute("DROP TABLE tree_adoptions")
                cur.execute("ALTER TABLE tree_adoptions_new RENAME TO tree_adoptions")
                cols = ['id','tree_id','user_id','adopter_name','adopted_at','health']
            # Ensure user_id set
            cur.execute("UPDATE tree_adoptions SET user_id = 'legacy' WHERE IFNULL(user_id,'') = ''")
            # Ensure uniqueness per (tree_id, user_id)
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tree_user_unique ON tree_adoptions(tree_id, user_id)")
            conn.commit()

    def get_for_tree(self, tree_id: int, user_id: str) -> Optional[Dict]:
        self.ensure_tables()
        q = "SELECT id, tree_id, adopter_name, adopted_at, health, user_id FROM tree_adoptions WHERE tree_id = ? AND user_id = ? ORDER BY id DESC LIMIT 1"
        rows = self.db.execute_query(q, (tree_id, user_id))
        if not rows:
            return None
        r = rows[0]
        return {
            'id': r[0],
            'tree_id': r[1],
            'adopter_name': r[2],
            'adopted_at': r[3],
            'health': int(r[4] or 0),
            'user_id': r[5],
        }

    def adopt_or_update(self, tree_id: int, user_id: str, adopter_name: str, health: int) -> Tuple[bool, str]:
        """Create or update adoption record for a tree."""
        self.ensure_tables()
        health = max(0, min(4, int(health or 0)))
        name = (adopter_name or '').strip()
        if not name:
            return False, 'Adopter name required'
        if not user_id:
            return False, 'Missing user id'

        existing = self.get_for_tree(tree_id, user_id)
        if existing:
            q = "UPDATE tree_adoptions SET adopter_name = ?, health = ? WHERE tree_id = ? AND user_id = ?"
            self.db.execute_write(q, (name, health, tree_id, user_id))
            return True, 'Adoption updated'
        else:
            q = (
                "INSERT INTO tree_adoptions (tree_id, user_id, adopter_name, adopted_at, health) "
                "VALUES (?, ?, ?, datetime('now'), ?)"
            )
            self.db.execute_write(q, (tree_id, user_id, name, health))
            return True, 'Tree adopted'

    def unadopt(self, tree_id: int, user_id: str) -> Tuple[bool, str]:
        self.ensure_tables()
        q = "DELETE FROM tree_adoptions WHERE tree_id = ? AND user_id = ?"
        self.db.execute_write(q, (tree_id, user_id))
        return True, 'Adoption removed'

    def list_for_user(self, user_id: str) -> list[Dict]:
        self.ensure_tables()
        q = (
            "SELECT ta.tree_id, ta.adopter_name, ta.adopted_at, ta.health, "
            "t.common_name, t.latin_name, t.latitude, t.longitude, t.dbh "
            "FROM tree_adoptions ta "
            "JOIN trees t ON t.tree_id = ta.tree_id "
            "WHERE ta.user_id = ? "
            "ORDER BY ta.adopted_at DESC"
        )
        rows = self.db.execute_query(q, (user_id,))
        out = []
        for r in rows:
            out.append({
                'tree_id': r[0],
                'adopter_name': r[1],
                'adopted_at': r[2],
                'health': int(r[3] or 0),
                'common_name': r[4],
                'latin_name': r[5],
                'latitude': r[6],
                'longitude': r[7],
                'dbh': r[8],
            })
        return out
