# routes/tree_routes.py
from flask import Blueprint, request, jsonify
from services.uk_tree_service import UKTreeService
from services.custom_tree_service import CustomTreeService
from services.adoption_service import AdoptionService
from services.damage_report_service import DamageReportService
from services.work_order_service import WorkOrderService
from services.invasive_service import InvasiveReportService
from services.volunteer_service import VolunteerService
import os

tree_routes = Blueprint('tree_routes', __name__)

# Initialize services
uk_service = UKTreeService()
custom_service = CustomTreeService()
adoption_service = AdoptionService()
damage_service = DamageReportService()
work_order_service = WorkOrderService()
invasive_service = InvasiveReportService()
volunteer_service = VolunteerService()

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

@tree_routes.route('/api/reports/user', methods=['GET'])
def list_reports_for_user():
    user_id = (request.args.get('user_id') or '').strip()
    if not user_id:
        return jsonify([])
    return jsonify(damage_service.list_for_user(user_id))

@tree_routes.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id: int):
    user_id = (request.args.get('user_id') or '').strip()
    if not user_id:
        return jsonify({'error': 'Missing user id'}), 400
    ok, msg = damage_service.delete_report(report_id, user_id)
    if ok:
        return jsonify({'message': msg})
    return jsonify({'error': msg}), 404

@tree_routes.route('/admin/reports/export.csv', methods=['GET'])
def export_reports_csv():
    since = request.args.get('since')  # optional ISO-8601 string yyyy-mm-dd or full datetime
    csv_text = damage_service.export_csv(since)
    headers = {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'attachment; filename="tree_damage_reports.csv"'
    }
    return csv_text, 200, headers

# Work Orders endpoints (public read-only subset)
@tree_routes.route('/api/work-orders/user', methods=['GET'])
def list_work_orders_for_user():
    user_id = (request.args.get('user_id') or '').strip()
    if not user_id:
        return jsonify([])
    return jsonify(work_order_service.list_for_user(user_id))

# Invasive plant report endpoints (greenspace; map-based)
@tree_routes.route('/api/invasives/report', methods=['POST'])
def submit_invasive_report():
    if not request.is_json:
        return jsonify({'error': 'Content type must be application/json'}), 400
    body = request.get_json() or {}
    user_id = (body.get('user_id') or '').strip()
    plant_type = (body.get('plant_type') or '').strip()
    note = (body.get('note') or '').strip()
    greenspace_name = (body.get('greenspace_name') or '').strip()
    try:
        lat = float(body.get('latitude'))
        lng = float(body.get('longitude'))
    except Exception:
        return jsonify({'error': 'Invalid or missing coordinates'}), 400
    ok, msg, rid = invasive_service.add(user_id=user_id, plant_type=plant_type, latitude=lat, longitude=lng, greenspace_name=greenspace_name, note=note)
    if ok:
        return jsonify({'message': msg, 'report_id': rid}), 201
    return jsonify({'error': msg}), 400


@tree_routes.route('/api/invasives/area', methods=['GET'])
def list_invasives_in_area():
    try:
        bounds = {
            'north': float(request.args.get('north')),
            'south': float(request.args.get('south')),
            'east': float(request.args.get('east')),
            'west': float(request.args.get('west'))
        }
    except Exception:
        return jsonify({'error': 'Invalid boundary parameters'}), 400
    return jsonify(invasive_service.list_in_bounds(**bounds))


@tree_routes.route('/api/volunteer/invasive', methods=['POST'])
def volunteer_for_invasive():
    if not request.is_json:
        return jsonify({'error': 'Content type must be application/json'}), 400
    body = request.get_json() or {}
    user_id = (body.get('user_id') or '').strip()
    plant_type = (body.get('plant_type') or '').strip() or 'invasive plant'
    greenspace_name = (body.get('greenspace_name') or '').strip()
    note_parts = []
    est_hours = (body.get('estimated_hours') or '').strip()
    when = (body.get('scheduled_at') or '').strip()
    custom_note = (body.get('note') or '').strip()
    if est_hours:
        note_parts.append(f"Est. {est_hours}h")
    if when:
        note_parts.append(f"When: {when}")
    if custom_note:
        note_parts.append(custom_note)
    note = ' | '.join([p for p in note_parts if p])
    try:
        lat = float(body.get('latitude'))
        lng = float(body.get('longitude'))
    except Exception:
        return jsonify({'error': 'Invalid or missing coordinates'}), 400

    task = f"Remove invasive: {plant_type}"
    ok, msg, req_id = volunteer_service.create(user_id=user_id, task=task, area_id=None, latitude=lat, longitude=lng, note=f"{greenspace_name} • {note}" if greenspace_name or note else note)
    # Create a corresponding work order for internal triage
    try:
        WorkOrderService().create_from_volunteer(user_id=user_id, task=task, latitude=lat, longitude=lng, area_name=greenspace_name, note=note)
    except Exception:
        pass
    if ok:
        return jsonify({'message': msg, 'request_id': req_id}), 201
    return jsonify({'error': msg}), 400


@tree_routes.route('/api/volunteer', methods=['POST'])
def volunteer_general():
    if not request.is_json:
        return jsonify({'error': 'Content type must be application/json'}), 400
    body = request.get_json() or {}
    user_id = (body.get('user_id') or '').strip()
    task = (body.get('task') or '').strip() or 'Volunteer service'
    greenspace_name = (body.get('greenspace_name') or '').strip()
    note_parts = []
    est_hours = (body.get('estimated_hours') or '').strip()
    when = (body.get('scheduled_at') or '').strip()
    custom_note = (body.get('note') or '').strip()
    if est_hours:
        note_parts.append(f"Est. {est_hours}h")
    if when:
        note_parts.append(f"When: {when}")
    if custom_note:
        note_parts.append(custom_note)
    note = ' | '.join([p for p in note_parts if p])
    try:
        lat = float(body.get('latitude'))
        lng = float(body.get('longitude'))
    except Exception:
        lat = None; lng = None
    ok, msg, req_id = volunteer_service.create(user_id=user_id, task=task, area_id=None, latitude=lat, longitude=lng, note=f"{greenspace_name} • {note}" if greenspace_name or note else note)
    try:
        WorkOrderService().create_from_volunteer(user_id=user_id, task=task, latitude=lat, longitude=lng, area_name=greenspace_name, note=note)
    except Exception:
        pass
    if ok:
        return jsonify({'message': msg, 'request_id': req_id}), 201
    return jsonify({'error': msg}), 400
