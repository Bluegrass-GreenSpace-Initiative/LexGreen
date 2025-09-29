from flask import Flask, jsonify, render_template, send_from_directory, request, redirect, url_for
from flask_cors import CORS
from flask_compress import Compress
from datetime import datetime
import os
from services.database import Database
from services.uk_tree_service import UKTreeService
from services.photo_service import PhotoService
from services.tree_facts import get_tree_fact
from werkzeug.utils import secure_filename
from services.staff_service import StaffService
from services.work_order_service import WorkOrderService
import html

app = Flask(__name__)
CORS(app)
Compress(app)

# Development configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = os.path.join('instance', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Campus data dictionary - main feature content
CAMPUS_DATA = {
    'map_layers': [
        {'id': 'buildings', 'name': 'Buildings'},
        {'id': 'spaces', 'name': 'Green Spaces'},
        {'id': 'paths', 'name': 'Paths'}
    ],
    'location_info': {
        'WT Young Library Lawn': {
            'description': 'An open space perfect for sunbathing and outdoor studying.',
            'features': ['Open Grass Area', 'Study Spots', 'WiFi Access', 'Natural Shade']
        },
        'President Garden': {
            'description': 'A serene garden featuring a beautiful lily pond and various native plants.',
            'features': ['Lily Pond', 'Native Plants', 'Benches', 'Shade Trees']
        }
    }
}

# Register blueprints
from routes.tree_routes import tree_routes
from routes.admin_routes import admin_bp
app.register_blueprint(tree_routes)
app.register_blueprint(admin_bp)

# Initialize database
@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    db = Database()
    conn = db.get_connection()
    with conn:
        cur = conn.cursor()
        # Ensure core trees table exists (compatible with CSV import)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trees (
                tree_id INTEGER PRIMARY KEY,
                common_name TEXT,
                latin_name TEXT,
                dbh REAL,
                latitude REAL,
                longitude REAL
            )
            """
        )
    # Ensure photos table exists
    PhotoService().ensure_tables()
    print('Initialized the database.')

@app.cli.command('import-trees')
def import_trees_command():
    """Import trees from CSV."""
    uk_service = UKTreeService()
    csv_path = os.path.join('data', 'UKTrees.csv')
    success, message = uk_service.import_uk_trees(csv_path)
    print(message)

@app.cli.command('create-staff')
def create_staff_command():
    """Create a staff user: supply EMAIL and PASSWORD env vars or be prompted."""
    import getpass
    email = os.environ.get('EMAIL') or input('Email: ').strip()
    name = os.environ.get('NAME') or ''
    password = os.environ.get('PASSWORD') or getpass.getpass('Password: ')
    ok, msg, sid = StaffService().create_staff(email, password, name=name)
    print(msg)

@app.cli.command('export-work-orders')
def export_work_orders_command():
    """Export work orders to CSV. Use SINCE (YYYY-MM-DD) and OUT path via env vars."""
    since = os.environ.get('SINCE')
    out = os.environ.get('OUT') or os.path.join('instance', 'exports', 'work_orders.csv')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    csv_text = WorkOrderService().export_csv(since)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(csv_text)
    print(f'Wrote {out}')

# Main routes
@app.route('/healthz')
def healthz():
    return 'ok', 200

@app.route('/')
def index():
    return render_template('index.html',
                         map_layers=CAMPUS_DATA['map_layers'],
                         location_info=CAMPUS_DATA['location_info'])

@app.route('/wellness')
def wellness():
    return render_template('wellness.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    # Render PRIVACY.md as simple HTML without extra dependencies
    md_path = os.path.join(os.path.dirname(__file__), 'PRIVACY.md')
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md = f.read().splitlines()
    except Exception:
        md = ["# Privacy Policy", "This page is temporarily unavailable."]

    html_parts = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append('</ul>')
            in_list = False

    for line in md:
        s = line.rstrip()
        if not s:
            close_list()
            continue
        if s.startswith('## '):
            close_list()
            html_parts.append(f"<h2>{html.escape(s[3:])}</h2>")
        elif s.startswith('# '):
            close_list()
            html_parts.append(f"<h1>{html.escape(s[2:])}</h1>")
        elif s.startswith('- '):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            html_parts.append(f"<li>{html.escape(s[2:])}</li>")
        else:
            close_list()
            html_parts.append(f"<p>{html.escape(s)}</p>")

    close_list()
    body_html = '\n'.join(html_parts)
    return render_template('privacy.html', body_html=body_html)

# Greenspace deep-dive page
@app.route('/greenspace')
def greenspace():
    name = request.args.get('name', 'Green Space')
    # Required bounds from query params
    try:
        bounds = {
            'north': float(request.args['north']),
            'south': float(request.args['south']),
            'east': float(request.args['east']),
            'west': float(request.args['west'])
        }
    except Exception:
        # If missing/invalid, just go home
        return redirect(url_for('index'))
    return render_template('greenspace.html', name=name, bounds=bounds)

@app.route('/my-adoptions')
def my_adoptions():
    # Render a page that fetches user-specific adoptions client-side
    return render_template('my_activity.html')

# Account deletion info page (for Play Console “Delete account URL”)
@app.route('/account-deletion')
def account_deletion():
    return render_template('account_deletion.html')

# Digital Asset Links for Android TWA (served at /.well-known/assetlinks.json)
@app.route('/.well-known/assetlinks.json')
def assetlinks():
    # Serve from static/.well-known; fill the file after running Bubblewrap
    return send_from_directory(os.path.join('static', '.well-known'), 'assetlinks.json')

# Tree detail page with photo gallery/upload
@app.route('/tree/<int:tree_id>')
def tree_detail(tree_id: int):
    tree = UKTreeService().get_tree_by_id(tree_id)
    if not tree:
        return render_template('tree_detail.html', tree=None, photos=[], fact=None, return_to=request.args.get('return_to')), 404
    photos = PhotoService().get_photos_for_tree(tree_id)
    fact = get_tree_fact(tree.get('common_name'), tree.get('latin_name'))
    return render_template('tree_detail.html', tree=tree, photos=photos, fact=fact, return_to=request.args.get('return_to'))

@app.route('/tree/<int:tree_id>/upload', methods=['POST'])
def upload_tree_photo(tree_id: int):
    # Basic validation that the tree exists
    if not UKTreeService().get_tree_by_id(tree_id):
        return redirect(url_for('index'))

    file = request.files.get('photo')
    if not file or file.filename == '':
        return redirect(url_for('tree_detail', tree_id=tree_id, return_to=request.args.get('return_to')))

    filename = secure_filename(file.filename)
    saved_name = PhotoService().save_photo(tree_id, file.stream, filename)
    # Record in DB
    PhotoService().add_photo_record(tree_id, saved_name)
    return_to = request.args.get('return_to')
    if return_to:
        return redirect(url_for('tree_detail', tree_id=tree_id, return_to=return_to))
    return redirect(url_for('tree_detail', tree_id=tree_id))

# Serve uploaded images
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Template context processor for global variables
@app.context_processor
def utility_processor():
    return {'current_year': datetime.now().year}

if __name__ == '__main__':
    app.run(debug=True)
