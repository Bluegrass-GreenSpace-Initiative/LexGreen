from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from .database import Database


class AmenityService:
    """Manage amenities such as benches, fountains, trash bins, etc."""

    def __init__(self) -> None:
        self.db = Database()

    def ensure_tables(self) -> None:
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS amenities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ok',
                    latitude REAL,
                    longitude REAL,
                    metadata TEXT,
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.commit()

    def list(self) -> List[Dict]:
        self.ensure_tables()
        rows = self.db.execute_query("SELECT id, name, type, status, latitude, longitude, metadata, updated_at FROM amenities ORDER BY updated_at DESC")
        return [
            {
                'id': r[0], 'name': r[1], 'type': r[2], 'status': r[3],
                'latitude': r[4], 'longitude': r[5], 'metadata': r[6], 'updated_at': r[7]
            }
            for r in rows
        ]

    def create(self, name: str, type_: str, status: str, latitude: Optional[float], longitude: Optional[float], metadata: Optional[str]) -> Tuple[bool, str, Optional[int]]:
        self.ensure_tables()
        if not name or not type_:
            return False, 'Name and type are required', None
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO amenities (name, type, status, latitude, longitude, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (name, type_, status or 'ok', latitude, longitude, metadata)
            )
            aid = cur.lastrowid
            conn.commit()
            return True, 'Amenity created', int(aid)

    def update(self, amenity_id: int, name: Optional[str], type_: Optional[str], status: Optional[str], latitude: Optional[float], longitude: Optional[float], metadata: Optional[str]) -> Tuple[bool, str]:
        self.ensure_tables()
        sets = []
        params: List = []  # type: ignore[name-defined]
        if name is not None:
            sets.append('name = ?'); params.append(name)
        if type_ is not None:
            sets.append('type = ?'); params.append(type_)
        if status is not None:
            sets.append('status = ?'); params.append(status)
        if latitude is not None:
            sets.append('latitude = ?'); params.append(latitude)
        if longitude is not None:
            sets.append('longitude = ?'); params.append(longitude)
        if metadata is not None:
            sets.append('metadata = ?'); params.append(metadata)
        if not sets:
            return True, 'No changes'
        sets.append("updated_at = datetime('now')")
        params.append(amenity_id)
        self.db.execute_write(f"UPDATE amenities SET {', '.join(sets)} WHERE id = ?", tuple(params))
        return True, 'Amenity updated'

    def delete(self, amenity_id: int) -> Tuple[bool, str]:
        self.ensure_tables()
        self.db.execute_write("DELETE FROM amenities WHERE id = ?", (amenity_id,))
        return True, 'Amenity deleted'

