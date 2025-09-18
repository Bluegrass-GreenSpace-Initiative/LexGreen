from __future__ import annotations

from flask import Blueprint, request, render_template, redirect, url_for, session, make_response
from typing import Optional
from services.staff_service import StaffService
from services.work_order_service import WorkOrderService
from services.amenity_service import AmenityService
from services.volunteer_service import VolunteerService


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _is_logged_in() -> bool:
    return bool(session.get('staff_id'))


@admin_bp.before_app_request
def _protect_admin():
    # Protect admin endpoints while keeping login accessible
    if request.path.startswith('/admin') and not request.path.startswith('/admin/login'):
        if not _is_logged_in():
            return redirect(url_for('admin.login', next=request.path))


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''
        ok, msg, staff = StaffService().verify_login(email, password)
        if ok and staff:
            session['staff_id'] = staff['id']
            session['staff_email'] = staff['email']
            nxt = request.args.get('next') or url_for('admin.dashboard')
            return redirect(nxt)
        return render_template('admin/login.html', error=msg)
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
def dashboard():
    status = request.args.get('status') or ''
    type_ = request.args.get('type') or ''
    orders = WorkOrderService().list(status=status or None, type_=type_ or None)
    return render_template('admin/dashboard.html', orders=orders, status=status, type_=type_)


@admin_bp.route('/work-orders/<int:wo_id>/update', methods=['POST'])
def update_work_order(wo_id: int):
    status = request.form.get('status') or None
    assigned_to = request.form.get('assigned_to') if 'assigned_to' in request.form else None
    resolution_note = request.form.get('resolution_note') if 'resolution_note' in request.form else None
    priority = request.form.get('priority')
    pr = int(priority) if priority else None
    WorkOrderService().update(wo_id, status=status, assigned_to=assigned_to, resolution_note=resolution_note, priority=pr)
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/work-orders/export.csv')
def export_work_orders_csv():
    since = request.args.get('since')
    csv_text = WorkOrderService().export_csv(since)
    resp = make_response(csv_text)
    resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
    resp.headers['Content-Disposition'] = 'attachment; filename="work_orders.csv"'
    return resp


# Amenities admin
@admin_bp.route('/amenities', methods=['GET', 'POST'])
def amenities():
    svc = AmenityService()
    if request.method == 'POST':
        name = request.form.get('name')
        type_ = request.form.get('type')
        status = request.form.get('status') or 'ok'
        lat = request.form.get('latitude'); latitude = float(lat) if lat else None
        lng = request.form.get('longitude'); longitude = float(lng) if lng else None
        metadata = request.form.get('metadata')
        svc.create(name, type_, status, latitude, longitude, metadata)
        return redirect(url_for('admin.amenities'))
    items = svc.list()
    return render_template('admin/amenities.html', items=items)


@admin_bp.route('/amenities/<int:aid>/update', methods=['POST'])
def amenities_update(aid: int):
    svc = AmenityService()
    name = request.form.get('name')
    type_ = request.form.get('type')
    status = request.form.get('status')
    lat = request.form.get('latitude'); latitude = float(lat) if lat else None
    lng = request.form.get('longitude'); longitude = float(lng) if lng else None
    metadata = request.form.get('metadata')
    svc.update(aid, name, type_, status, latitude, longitude, metadata)
    return redirect(url_for('admin.amenities'))


@admin_bp.route('/amenities/<int:aid>/delete', methods=['POST'])
def amenities_delete(aid: int):
    AmenityService().delete(aid)
    return redirect(url_for('admin.amenities'))


# Volunteer approvals
@admin_bp.route('/volunteers', methods=['GET', 'POST'])
def volunteers():
    svc = VolunteerService()
    if request.method == 'POST':
        # create endpoint could be added later; for now, admin manages statuses only
        pass
    items = svc.list()
    return render_template('admin/volunteers.html', items=items)


@admin_bp.route('/volunteers/<int:vid>/update', methods=['POST'])
def volunteers_update(vid: int):
    status = request.form.get('status')
    permit_from = request.form.get('permit_valid_from')
    permit_to = request.form.get('permit_valid_to')
    VolunteerService().update(vid, status=status, permit_valid_from=permit_from, permit_valid_to=permit_to)
    return redirect(url_for('admin.volunteers'))
