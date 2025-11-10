from __future__ import annotations

import os
import html
from typing import Dict
from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, current_app
from services.uk_tree_service import UKTreeService
from services.photo_service import PhotoService
from services.tree_facts import get_tree_fact
from services.tree_morphology import get_leaf_info, get_bark_info
from werkzeug.utils import secure_filename


pages_bp = Blueprint('pages', __name__)


# Campus data dictionary - main feature content
CAMPUS_DATA: Dict = {
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
        },
        'Gatton College of Business Greenspace': {
            'description': 'A greenspace filled with tree that praovide shade and a few gardens around the building.',
            'features': ['Shade Trees', 'Gardens']
        },
        'Adminstration Drive Lawn': {
            'description': 'An open space near the edge of campus that leads to the center of the UK campus.',
            'features': ['Open Grass Area','Bus Stop for 5, 14, and 15','Nearby Parking Garage']
        },
        'Student Center Outdoor Pathway': {
            'description': 'A pathway along a slope between Patterson Drive and the first floor exit of the Student Center.',
            'features': ['Benches', 'Less Crowded']
        },
        'Signletary Center Lawn': {
            'description': 'A flat open area with art pieces dotted about.',
            'features': ['Art Installations', 'Shade Trees', 'Benches']
        },
        'Student Center Outdoor Seating': {
            'description': 'A small area outside the Student Center with seating.',
            'features': ['Nearby Food', 'Seating','Bike Racks']
        },
        'Funkhouser Walkway': {
            'description': 'A shaded path that accesses the main entrance of Funkhouser.',
            'features': ['Shaded Trees','Study Spots', 'Benches']
        }
    }
}


@pages_bp.route('/healthz')
def healthz():
    return 'ok', 200


@pages_bp.route('/')
def index():
    return render_template('index.html',
                           map_layers=CAMPUS_DATA['map_layers'],
                           location_info=CAMPUS_DATA['location_info'])


@pages_bp.route('/wellness')
def wellness():
    return render_template('wellness.html')


@pages_bp.route('/about')
def about():
    return render_template('about.html')


@pages_bp.route('/privacy')
def privacy():
    # Render PRIVACY.md as simple HTML without extra dependencies
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    md_path = os.path.join(root, 'PRIVACY.md')
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
            close_list();
            continue
        if s.startswith('## '):
            close_list(); html_parts.append(f"<h2>{html.escape(s[3:])}</h2>")
        elif s.startswith('# '):
            close_list(); html_parts.append(f"<h1>{html.escape(s[2:])}</h1>")
        elif s.startswith('- '):
            if not in_list:
                html_parts.append('<ul>'); in_list = True
            html_parts.append(f"<li>{html.escape(s[2:])}</li>")
        else:
            close_list(); html_parts.append(f"<p>{html.escape(s)}</p>")

    close_list()
    body_html = '\n'.join(html_parts)
    return render_template('privacy.html', body_html=body_html)


@pages_bp.route('/greenspace')
def greenspace():
    name = request.args.get('name', 'Green Space')
    try:
        bounds = {
            'north': float(request.args['north']),
            'south': float(request.args['south']),
            'east': float(request.args['east']),
            'west': float(request.args['west'])
        }
    except Exception:
        return redirect(url_for('pages.index'))
    # Pass simple meta (description/features) when available so the page
    # can render lightweight amenities and suggestions without new APIs.
    gs_meta = CAMPUS_DATA.get('location_info', {}).get(name)
    return render_template('greenspace.html', name=name, bounds=bounds, gs_meta=gs_meta)


@pages_bp.route('/my-adoptions')
def my_adoptions():
    return render_template('my_activity.html')


@pages_bp.route('/account-deletion')
def account_deletion():
    return render_template('account_deletion.html')


@pages_bp.route('/.well-known/assetlinks.json')
def assetlinks():
    # Serve from static/.well-known; fill the file after running Bubblewrap
    root = current_app.static_folder
    return send_from_directory(os.path.join(root, '.well-known'), 'assetlinks.json')


@pages_bp.route('/tree/<int:tree_id>')
def tree_detail(tree_id: int):
    tree = UKTreeService().get_tree_by_id(tree_id)
    if not tree:
        return render_template('tree_detail.html', tree=None, photos=[], fact=None, leaf_info=None, bark_info=None, return_to=request.args.get('return_to')), 404
    photos = PhotoService().get_photos_for_tree(tree_id)
    fact = get_tree_fact(tree.get('common_name'), tree.get('latin_name'))
    leaf_info = get_leaf_info(tree.get('common_name'), tree.get('latin_name'))
    bark_info = get_bark_info(tree.get('common_name'), tree.get('latin_name'))
    return render_template(
        'tree_detail.html',
        tree=tree,
        photos=photos,
        fact=fact,
        leaf_info=leaf_info,
        bark_info=bark_info,
        return_to=request.args.get('return_to'),
    )


@pages_bp.route('/tree/<int:tree_id>/upload', methods=['POST'])
def upload_tree_photo(tree_id: int):
    if not UKTreeService().get_tree_by_id(tree_id):
        return redirect(url_for('pages.index'))

    file = request.files.get('photo')
    if not file or file.filename == '':
        return redirect(url_for('pages.tree_detail', tree_id=tree_id, return_to=request.args.get('return_to')))

    filename = secure_filename(file.filename)
    _, ext = os.path.splitext(filename.lower())
    if ext.lstrip('.') not in {'jpg', 'jpeg', 'png', 'webp'}:
        return redirect(url_for('pages.tree_detail', tree_id=tree_id, return_to=request.args.get('return_to')))

    saved_name = PhotoService().save_photo(tree_id, file.stream, filename)
    PhotoService().add_photo_record(tree_id, saved_name)
    return_to = request.args.get('return_to')
    if return_to:
        return redirect(url_for('pages.tree_detail', tree_id=tree_id, return_to=return_to))
    return redirect(url_for('pages.tree_detail', tree_id=tree_id))


@pages_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
