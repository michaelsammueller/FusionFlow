from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.database import SessionLocal
from backend.models import User, Project, Order, Shipment
from backend.models.notifications import Notification
from datetime import datetime
from sqlalchemy import desc
from backend.models.audit_log import AuditLog

users_bp = Blueprint('users', __name__, url_prefix='/users')

def get_db():
    return SessionLocal()

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('users.list_users'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'manager':
            flash('Manager access required.', 'danger')
            return redirect(url_for('users.list_users'))
        return f(*args, **kwargs)
    return decorated_function

@users_bp.route('/')
@login_required
def list_users():
    allowed_roles = ['admin', 'manager', 'associate_project_manager', 'project_manager', 'senior_project_manager', 'engineering_manager', 'design_manager']
    if current_user.role not in allowed_roles:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    db = get_db()
    try:
        users = db.query(User).filter(User.is_active == True).order_by(User.full_name).all()
        return render_template('users/list.html', users=users)
    finally:
        db.close()

@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    db = get_db()
    try:
        if request.method == 'POST':
            full_name = request.form.get('full_name')
            username = request.form.get('username')
            email = request.form.get('email')
            role = request.form.get('role')
            department = request.form.get('department')
            password = request.form.get('password')
            if not all([full_name, username, email, role, password]):
                flash('All fields are required.', 'danger')
                return render_template('users/add.html')
            # Check for existing username or email
            existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash('A user with that username or email already exists.', 'danger')
                return render_template('users/add.html')
            from backend.auth import get_password_hash
            hashed_password = get_password_hash(password)
            new_user = User(
                full_name=full_name,
                username=username,
                email=email,
                role=role,
                department=department,
                hashed_password=hashed_password,
                is_active=True
            )
            db.add(new_user)
            db.commit()
            flash('User added successfully.', 'success')
            return redirect(url_for('users.list_users'))
        return render_template('users/add.html')
    finally:
        db.close()

@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            flash('User not found.', 'danger')
        elif user.role == 'admin':
            flash('Cannot delete another admin.', 'danger')
        else:
            db.delete(user)
            db.commit()
            flash('User deleted.', 'success')
        return redirect(url_for('users.list_users'))
    finally:
        db.close()

@users_bp.route('/<int:user_id>/assign', methods=['GET', 'POST'])
@login_required
def assign_user(user_id):
    allowed_roles = [
        'admin',
        'manager',
        'engineering_manager',
        'project_manager',
        'senior_project_manager',
        'associate_project_manager',
        'design_manager'
    ]
    if current_user.role not in allowed_roles:
        flash('Access denied.', 'danger')
        return redirect(url_for('users.list_users'))
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('users.list_users'))
        projects = db.query(Project).order_by(Project.name).all()
        orders = db.query(Order).order_by(Order.order_number).all()
        shipments = db.query(Shipment).order_by(Shipment.tracking_number).all()
        if request.method == 'POST':
            project_id = request.form.get('project_id')
            order_id = request.form.get('order_id')
            shipment_id = request.form.get('shipment_id')
            assigned = False
            if project_id:
                project = db.query(Project).get(int(project_id))
                if project:
                    project.assigned_user_id = user.id
                    project.assigned_by = current_user.full_name
                    assigned = True
                    notif = Notification(
                        user_id=user.id,
                        notification_type='Assignment',
                        title='Assigned to Project',
                        message=f'You have been assigned to project "{project.name}" by {current_user.full_name}.',
                        action_url=url_for('projects.view_project', project_id=project.id),
                        action_button_text='View Project',
                        created_at=datetime.utcnow()
                    )
                    db.add(notif)
            if order_id:
                order = db.query(Order).get(int(order_id))
                if order:
                    order.assigned_user_id = user.id
                    order.assigned_by = current_user.full_name
                    assigned = True
                    notif = Notification(
                        user_id=user.id,
                        notification_type='Assignment',
                        title='Assigned to Order',
                        message=f'You have been assigned to order "{order.order_number}" by {current_user.full_name}.',
                        action_url=url_for('orders.view_order', order_id=order.id),
                        action_button_text='View Order',
                        created_at=datetime.utcnow()
                    )
                    db.add(notif)
            if shipment_id:
                shipment = db.query(Shipment).get(int(shipment_id))
                if shipment:
                    shipment.assigned_user_id = user.id
                    shipment.assigned_by = current_user.full_name
                    assigned = True
                    notif = Notification(
                        user_id=user.id,
                        notification_type='Assignment',
                        title='Assigned to Shipment',
                        message=f'You have been assigned to shipment "{shipment.tracking_number}" by {current_user.full_name}.',
                        action_url=url_for('shipments.view_shipment', shipment_id=shipment.id),
                        action_button_text='View Shipment',
                        created_at=datetime.utcnow()
                    )
                    db.add(notif)
            if assigned:
                db.commit()
                flash('User assignments updated and notification sent.', 'success')
            else:
                flash('No assignment selected.', 'warning')
            return redirect(url_for('users.list_users'))
        return render_template('users/assign.html', user=user, projects=projects, orders=orders, shipments=shipments)
    finally:
        db.close()

@users_bp.route('/assignments')
@login_required
def assignments():
    db = get_db()
    try:
        projects = db.query(Project).filter(Project.assigned_user_id == current_user.id).all()
        orders = db.query(Order).filter(Order.assigned_user_id == current_user.id).all()
        shipments = db.query(Shipment).filter(Shipment.assigned_user_id == current_user.id).all()
        # Pass assigned_by for each
        projects = [{**p.__dict__, 'assigned_by': p.assigned_by} for p in projects]
        orders = [{**o.__dict__, 'assigned_by': o.assigned_by} for o in orders]
        shipments = [{**s.__dict__, 'assigned_by': s.assigned_by} for s in shipments]
        return render_template('users/assignments.html', projects=projects, orders=orders, shipments=shipments)
    finally:
        db.close()

@users_bp.route('/logs')
@login_required
def logs():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    db = get_db()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
        return render_template('users/logs.html', logs=logs)
    finally:
        db.close()

@users_bp.route('/notifications/unread', methods=['GET', 'POST'])
@login_required
def unread_notifications():
    db = get_db()
    try:
        if request.method == 'POST':
            notifs = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).all()
            for n in notifs:
                n.is_read = True
                n.read_at = datetime.utcnow()
            db.commit()
            return '', 204
        notifs = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).order_by(Notification.created_at.desc()).all()
        notif_list = [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'action_url': n.action_url,
                'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
            } for n in notifs
        ]
        return jsonify({'unread': notif_list})
    finally:
        db.close()

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('users.list_users'))
        if request.method == 'POST':
            user.full_name = request.form.get('full_name', user.full_name)
            user.username = request.form.get('username', user.username)
            user.email = request.form.get('email', user.email)
            user.role = request.form.get('role', user.role)
            user.department = request.form.get('department', user.department)
            user.is_active = bool(request.form.get('is_active', user.is_active))
            try:
                db.commit()
                flash('User updated successfully.', 'success')
                return redirect(url_for('users.list_users'))
            except Exception as e:
                db.rollback()
                flash('An error occurred while updating the user.', 'danger')
        return render_template('users/edit.html', user=user)
    finally:
        db.close() 