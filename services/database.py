# services/database.py
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Tuple, List
import math
import pandas as pd

class Database:
    def __init__(self):
        self.db_path = 'instance/UKTrees.db'

    def _resolve_db_path(self) -> str:
        """Prefer Flask config DATABASE when available, fallback to default path."""
        try:
            # Import inside method to avoid hard dependency at import time
            from flask import current_app
            if current_app and current_app.config.get('DATABASE'):
                return current_app.config['DATABASE']
        except Exception:
            pass
        return self.db_path
    
    def get_connection(self) -> Connection:
        """Create and return a database connection"""
        return sqlite3.connect(self._resolve_db_path())
    
    def execute_query(self, query: str, params: Tuple = ()) -> list:
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_write(self, query: str, params: Tuple = ()) -> int:
        """Execute an insert/update query and return last row id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def bulk_insert_from_df(self, table_name: str, df: pd.DataFrame) -> None:
        """Insert data from a pandas DataFrame"""
        with self.get_connection() as conn:
            df.to_sql(table_name, conn, if_exists='append', index=False)
    
    def get_all_from_table(self, table_name: str) -> list:
        """Get all records from a table"""
        query = f"SELECT * FROM {table_name}"
        return self.execute_query(query)
    
    def get_by_id(self, table_name: str, id: int) -> tuple:
        """Get a single record by ID"""
        query = f"SELECT * FROM {table_name} WHERE tree_id = ?"
        result = self.execute_query(query, (id,))
        return result[0] if result else None

    def get_tree_count(self) -> int:
        """Get total number of trees"""
        query = "SELECT COUNT(*) FROM trees"
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    def get_trees_in_radius(self, lat: float, lng: float, radius_km: float) -> list:
        """Get trees within radius of point (SQLite-safe).

        SQLite lacks trigonometric functions by default, so we avoid computing distance in SQL.
        Strategy: do a quick bounding-box filter in SQL, then compute precise haversine distance
        in Python, filter/sort, and return rows appended with distance at index 6 to match
        callers that expect it.
        """
        # Approx degree deltas
        lat_rad = math.radians(lat)
        dlat = radius_km / 111.32
        # Guard against cos(±90°) -> 0
        dlon = radius_km / max(1e-6, (111.32 * math.cos(lat_rad)))

        min_lat, max_lat = lat - dlat, lat + dlat
        min_lng, max_lng = lng - dlon, lng + dlon

        # Fetch candidates from bounding box
        rows = self.execute_query(
            """
            SELECT tree_id, common_name, latin_name, dbh, latitude, longitude
            FROM trees
            WHERE latitude BETWEEN ? AND ?
              AND longitude BETWEEN ? AND ?
            """,
            (min_lat, max_lat, min_lng, max_lng)
        )

        def hav_km(lat1, lon1, lat2, lon2) -> float:
            R = 6371.0
            dphi = math.radians(lat2 - lat1)
            dlmb = math.radians(lon2 - lon1)
            a = math.sin(dphi/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlmb/2)**2
            return 2 * R * math.asin(math.sqrt(a))

        out: List[tuple] = []
        for r in rows:
            rlat, rlng = float(r[4] or 0.0), float(r[5] or 0.0)
            dist = hav_km(lat, lng, rlat, rlng)
            if dist <= radius_km:
                out.append((*r, dist))

        # Sort by distance ascending
        out.sort(key=lambda t: t[6])
        return out
