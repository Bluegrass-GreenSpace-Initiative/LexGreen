from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple


@dataclass
class InvasiveReport:
    id: int
    user_id: str
    plant_type: str
    latitude: float
    longitude: float
    greenspace_name: str
    note: str
    reported_at: str


class InvasiveReportService:
    """Persist invasive plant reports to a CSV file and list by map area bounds.

    CSV schema:
      id,user_id,plant_type,latitude,longitude,greenspace_name,note,reported_at
    """

    def __init__(self, instance_dir: Optional[str] = None) -> None:
        # Default to the Flask instance directory if present; otherwise use local ./instance
        base = instance_dir or os.path.join(os.getcwd(), 'instance')
        os.makedirs(base, exist_ok=True)
        self.csv_path = os.path.join(base, 'invasive_reports.csv')
        self._ensure_csv()

    def _ensure_csv(self) -> None:
        if not os.path.exists(self.csv_path):
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                w = csv.writer(f)
                w.writerow(['id', 'user_id', 'plant_type', 'latitude', 'longitude', 'greenspace_name', 'note', 'reported_at'])

    def _next_id(self) -> int:
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                r = csv.reader(f)
                header = next(r, None)
                last = 0
                for row in r:
                    try:
                        last = max(last, int(row[0]))
                    except Exception:
                        continue
                return last + 1
        except Exception:
            return 1

    def add(self, *, user_id: str, plant_type: str, latitude: float, longitude: float, greenspace_name: str, note: str = '') -> Tuple[bool, str, Optional[int]]:
        plant = (plant_type or '').strip() or 'unspecified'
        uid = (user_id or '').strip()
        if not uid:
            return False, 'Missing user id', None
        try:
            lat = float(latitude)
            lng = float(longitude)
        except Exception:
            return False, 'Invalid coordinates', None
        name = (greenspace_name or '').strip()
        now = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        rid = self._next_id()
        with open(self.csv_path, 'a', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow([rid, uid, plant, f'{lat:.6f}', f'{lng:.6f}', name, note or '', now])
        return True, 'Report submitted', rid

    def list_in_bounds(self, *, north: float, south: float, east: float, west: float) -> List[Dict]:
        """Return all reports whose lat/lng fall within the provided bounds."""
        out: List[Dict] = []
        try:
            n = float(north); s = float(south); e = float(east); w = float(west)
        except Exception:
            return out
        if s > n: s, n = n, s
        if w > e: w, e = e, w
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                r = csv.DictReader(f)
                for row in r:
                    try:
                        lat = float(row['latitude']); lng = float(row['longitude'])
                    except Exception:
                        continue
                    if (s <= lat <= n) and (w <= lng <= e):
                        out.append({
                            'id': int(row['id']),
                            'user_id': row['user_id'],
                            'plant_type': row['plant_type'],
                            'latitude': lat,
                            'longitude': lng,
                            'greenspace_name': row.get('greenspace_name') or '',
                            'note': row.get('note') or '',
                            'reported_at': row.get('reported_at') or ''
                        })
        except FileNotFoundError:
            # no reports yet
            return []
        except Exception:
            # On parse error, return what we have
            return out
        # Newest first by id
        out.sort(key=lambda x: x['id'], reverse=True)
        return out

    def list_all(self) -> List[Dict]:
        """Return all invasive reports, newest first by id."""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                r = csv.DictReader(f)
                items: List[Dict] = []
                for row in r:
                    try:
                        items.append({
                            'id': int(row['id']),
                            'user_id': row['user_id'],
                            'plant_type': row['plant_type'],
                            'latitude': float(row['latitude']),
                            'longitude': float(row['longitude']),
                            'greenspace_name': row.get('greenspace_name') or '',
                            'note': row.get('note') or '',
                            'reported_at': row.get('reported_at') or ''
                        })
                    except Exception:
                        continue
                items.sort(key=lambda x: x['id'], reverse=True)
                return items
        except FileNotFoundError:
            return []

    def export_csv(self) -> str:
        """Return CSV text for all invasive reports."""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return 'id,user_id,plant_type,latitude,longitude,greenspace_name,note,reported_at\n'

    def delete(self, report_id: int) -> Tuple[bool, str]:
        """Delete a report by id from the CSV file."""
        try:
            rows: List[List[str]] = []
            removed = False
            with open(self.csv_path, 'r', encoding='utf-8', newline='') as f:
                r = csv.reader(f)
                header = next(r, None)
                if header:
                    rows.append(header)
                for row in r:
                    try:
                        rid = int(row[0])
                    except Exception:
                        rid = None
                    if rid == report_id:
                        removed = True
                        continue
                    rows.append(row)
            with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                w = csv.writer(f)
                for row in rows:
                    w.writerow(row)
            if removed:
                return True, 'Deleted'
            return False, 'Not found'
        except FileNotFoundError:
            return False, 'Not found'
        except Exception:
            return False, 'Failed to delete'
