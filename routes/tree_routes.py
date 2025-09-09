# routes/tree_routes.py
from flask import Blueprint, request, jsonify
from services.uk_tree_service import UKTreeService
from services.custom_tree_service import CustomTreeService
from services.adoption_service import AdoptionService
from services.damage_report_service import DamageReportService
import os

tree_routes = Blueprint('tree_routes', __name__)

# Initialize services
uk_service = UKTreeService()
custom_service = CustomTreeService()
adoption_service = AdoptionService()
damage_service = DamageReportService()

# GET routes for retrieving tree data
@tree_routes.route('/api/trees', methods=['GET'])
def get_trees():
    """Get all trees"""
    return jsonify(uk_service.get_all_trees())

@tree_routes.route('/api/trees/geojson', methods=['GET'])
def get_trees_geojson():
    """Get trees in GeoJSON format for mapping"""
    return jsonify(uk_service.get_trees_geojson())

@tree_routes.route('/api/trees/<int:tree_id>', methods=['GET'])
def get_tree(tree_id):
    """Get single tree by ID"""
    tree = uk_service.get_tree_by_id(tree_id)
    if tree:
        return jsonify(tree)
    return jsonify({'error': 'Tree not found'}), 404

@tree_routes.route('/api/trees/species/<species>', methods=['GET'])
def get_trees_by_species(species):
    """Get trees by species"""
    trees = uk_service.get_trees_by_species(species)
    return jsonify(trees)

@tree_routes.route('/api/trees/nearby', methods=['GET'])
def get_nearby_trees():
    """Get trees near a location"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 0.5))
        trees = custom_service.get_nearby_trees(lat, lng, radius)
        return jsonify(trees)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid location parameters'}), 400

@tree_routes.route('/api/trees/species/count', methods=['GET'])
def get_species_count():
    """Get count of trees by species"""
    return jsonify(uk_service.get_species_count())

# POST routes for adding/modifying tree data
@tree_routes.route('/api/trees', methods=['POST'])
def add_tree():
    """Add a new tree"""
    if not request.is_json:
        return jsonify({'error': 'Content type must be application/json'}), 400
    
    tree_data = request.get_json()
    success, message, tree_id = custom_service.add_tree(tree_data)
    
    if success:
        return jsonify({
            'message': message,
            'tree_id': tree_id
        }), 201
    return jsonify({'error': message}), 400

@tree_routes.route('/api/trees/<int:tree_id>', methods=['PUT'])
def update_tree(tree_id):
    """Update existing tree"""
    if not request.is_json:
        return jsonify({'error': 'Content type must be application/json'}), 400
    
    tree_data = request.get_json()
    success, message = custom_service.update_tree(tree_id, tree_data)
    
    if success:
        return jsonify({'message': message})
    return jsonify({'error': message}), 400

@tree_routes.route('/api/trees/<int:tree_id>', methods=['DELETE'])
def delete_tree(tree_id):
    """Delete a tree"""
    success, message = custom_service.delete_tree(tree_id)
    if success:
        return jsonify({'message': message})
    return jsonify({'error': message}), 404

# Data import routes
@tree_routes.route('/api/import/uk-trees', methods=['POST'])
def import_uk_trees():
    """Import official UK trees data"""
    csv_path = os.path.join('data', 'UKTrees.csv')
    if not os.path.exists(csv_path):
        return jsonify({'error': 'UKTrees.csv not found'}), 404
    
    success, message = uk_service.import_uk_trees(csv_path)
    if success:
        return jsonify({'message': message})
    return jsonify({'error': message}), 400

# Area-based queries
@tree_routes.route('/api/trees/area', methods=['GET'])
def get_trees_in_area():
    """Get trees within map bounds"""
    try:
        bounds = {
            'north': float(request.args.get('north')),
            'south': float(request.args.get('south')),
            'east': float(request.args.get('east')),
            'west': float(request.args.get('west'))
        }
        trees = uk_service.get_trees_in_area(bounds)
        return jsonify(trees)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid boundary parameters'}), 400

# Adoption endpoints
@tree_routes.route('/api/adoption/<int:tree_id>', methods=['GET'])
def get_adoption(tree_id: int):
    user_id = request.args.get('user_id', '').strip()
    if not user_id:
        return jsonify({})
    data = adoption_service.get_for_tree(tree_id, user_id)
    return jsonify(data or {})

@tree_routes.route('/api/adoption/<int:tree_id>', methods=['POST'])
def upsert_adoption(tree_id: int):
    if not request.is_json:
        return jsonify({'error': 'Content type must be application/json'}), 400
    body = request.get_json() or {}
    adopter_name = body.get('adopter_name')
    health = body.get('health', 0)
    user_id = (body.get('user_id') or '').strip()
    ok, msg = adoption_service.adopt_or_update(tree_id, user_id, adopter_name, health)
    if ok:
        return jsonify({'message': msg, 'adoption': adoption_service.get_for_tree(tree_id, user_id)})
    return jsonify({'error': msg}), 400

@tree_routes.route('/api/adoption/<int:tree_id>', methods=['DELETE'])
def delete_adoption(tree_id: int):
    user_id = request.args.get('user_id', '').strip()
    if not user_id:
        return jsonify({'error': 'Missing user id'}), 400
    ok, msg = adoption_service.unadopt(tree_id, user_id)
    if ok:
        return jsonify({'message': msg})
    return jsonify({'error': msg}), 400

@tree_routes.route('/api/adoptions', methods=['GET'])
def list_adoptions():
    user_id = request.args.get('user_id', '').strip()
    if not user_id:
        return jsonify([])
    return jsonify(adoption_service.list_for_user(user_id))

# Damage report endpoints
@tree_routes.route('/api/reports', methods=['POST'])
def submit_report():
    if not request.is_json:
        return jsonify({'error': 'Content type must be application/json'}), 400
    body = request.get_json() or {}
    try:
        tree_id = int(body.get('tree_id'))
    except Exception:
        return jsonify({'error': 'Missing or invalid tree_id'}), 400
    user_id = (body.get('user_id') or '').strip()
    issue_type = body.get('issue_type')
    severity = body.get('severity', 1)
    description = body.get('description', '')
    ok, msg, rid = damage_service.add_report(tree_id, user_id, issue_type, severity, description)
    if ok:
        return jsonify({'message': msg, 'report_id': rid}), 201
    return jsonify({'error': msg}), 400

@tree_routes.route('/api/reports/<int:tree_id>', methods=['GET'])
def list_reports_for_tree(tree_id: int):
    return jsonify(damage_service.list_for_tree(tree_id))

@tree_routes.route('/admin/reports/export.csv', methods=['GET'])
def export_reports_csv():
    since = request.args.get('since')  # optional ISO-8601 string yyyy-mm-dd or full datetime
    csv_text = damage_service.export_csv(since)
    headers = {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'attachment; filename="tree_damage_reports.csv"'
    }
    return csv_text, 200, headers
