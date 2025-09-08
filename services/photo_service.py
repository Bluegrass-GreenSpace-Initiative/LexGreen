from __future__ import annotations

import os
import time
from typing import List, Dict
from .database import Database


class PhotoService:
    def __init__(self, upload_root: str = os.path.join('instance', 'uploads')):
        self.db = Database()
        self.upload_root = upload_root
        os.makedirs(self.upload_root, exist_ok=True)

    def ensure_tables(self) -> None:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tree_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tree_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    FOREIGN KEY(tree_id) REFERENCES trees(tree_id)
                )
                """
            )
            conn.commit()

    def _tree_dir(self, tree_id: int) -> str:
        d = os.path.join(self.upload_root, 'trees', str(tree_id))
        os.makedirs(d, exist_ok=True)
        return d

    def save_photo(self, tree_id: int, stream, original_filename: str) -> str:
        base, ext = os.path.splitext(original_filename)
        ts = int(time.time())
        safe = f"{ts}_{base[:64]}{ext.lower()}"
        path = os.path.join(self._tree_dir(tree_id), safe)
        with open(path, 'wb') as f:
            f.write(stream.read())
        # Return path relative to upload root so it can be served
        rel = os.path.relpath(path, self.upload_root)
        return rel.replace('\\', '/')

    def add_photo_record(self, tree_id: int, relative_filename: str) -> None:
        self.ensure_tables()
        q = (
            "INSERT INTO tree_photos (tree_id, filename, uploaded_at) "
            "VALUES (?, ?, datetime('now'))"
        )
        self.db.execute_write(q, (tree_id, relative_filename))

    def get_photos_for_tree(self, tree_id: int) -> List[Dict]:
        self.ensure_tables()
        q = "SELECT id, filename, uploaded_at FROM tree_photos WHERE tree_id = ? ORDER BY uploaded_at DESC"
        rows = self.db.execute_query(q, (tree_id,))
        return [
            {
                'id': r[0],
                'filename': r[1],
                'url': f"/uploads/{r[1]}",
                'uploaded_at': r[2],
            }
            for r in rows
        ]

