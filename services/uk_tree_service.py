# services/uk_tree_service.py
from .database import Database
import pandas as pd
from typing import List, Dict, Optional, Tuple

class UKTreeService:
    SELECT_COLS = "tree_id, common_name, latin_name, dbh, latitude, longitude"

    def __init__(self):
        self.db = Database()

    def get_all_trees(self) -> List[Dict]:
        """Get all trees with formatted output"""
        query = f"SELECT {self.SELECT_COLS} FROM trees"
        trees = self.db.execute_query(query)
        return [self._format_tree(tree) for tree in trees]

    def get_tree_by_id(self, tree_id: int) -> Optional[Dict]:
        """Get single tree by ID"""
        query = f"SELECT {self.SELECT_COLS} FROM trees WHERE tree_id = ?"
        result = self.db.execute_query(query, (tree_id,))
        return self._format_tree(result[0]) if result else None

    def get_trees_by_species(self, latin_name: str) -> List[Dict]:
        """Get all trees of a specific species"""
        query = f"SELECT {self.SELECT_COLS} FROM trees WHERE latin_name LIKE ?"
        trees = self.db.execute_query(query, (f"%{latin_name}%",))
        return [self._format_tree(tree) for tree in trees]

    def get_trees_in_area(self, bounds: Dict[str, float]) -> List[Dict]:
        """Get trees within map bounds"""
        query = f"""
        SELECT {self.SELECT_COLS} FROM trees
        WHERE latitude BETWEEN ? AND ?
          AND longitude BETWEEN ? AND ?
        """
        params = (
            bounds['south'], bounds['north'],
            bounds['west'], bounds['east']
        )
        trees = self.db.execute_query(query, params)
        return [self._format_tree(tree) for tree in trees]

    def import_uk_trees(self, csv_path: str) -> Tuple[bool, str]:
        """Import trees from official CSV file"""
        try:
            df = pd.read_csv(csv_path)
            # Clean column names
            df.columns = [
                'common_name', 'latin_name', 'dbh',
                'latitude', 'longitude', 'tree_id'
            ]
            
            self.db.bulk_insert_from_df('trees', df)
            return True, f"Successfully imported {len(df)} trees"
        except Exception as e:
            return False, f"Error importing trees: {str(e)}"

    def get_species_count(self) -> Dict[str, int]:
        """Get count of trees by species"""
        query = """
        SELECT latin_name, COUNT(*) as count
        FROM trees
        GROUP BY latin_name
        ORDER BY count DESC
        """
        results = self.db.execute_query(query)
        return {row[0]: row[1] for row in results}

    def _format_tree(self, tree_tuple: tuple) -> Dict:
        """Convert tree tuple to dictionary"""
        return {
            'tree_id': tree_tuple[0],
            'common_name': tree_tuple[1],
            'latin_name': tree_tuple[2],
            'dbh': tree_tuple[3],
            'latitude': tree_tuple[4],
            'longitude': tree_tuple[5],
            'properties': {  # GeoJSON properties
                'title': tree_tuple[1],
                'description': f"{tree_tuple[2]} (DBH: {tree_tuple[3]}cm)"
            }
        }

    def get_trees_geojson(self) -> Dict:
        """Get trees in GeoJSON format for mapping"""
        trees = self.get_all_trees()
        return {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [tree['longitude'], tree['latitude']]
                },
                'properties': tree['properties']
            } for tree in trees]
        }
