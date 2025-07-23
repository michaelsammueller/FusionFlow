from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from backend.database import SessionLocal
from backend.models import User, Project, Supplier, Order, Shipment, Document

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-shall-not-pass-bossm@n-1800'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///./fusionflow.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    try:
        user = db.query(User).get(int(user_id))
        return user
    finally:
        db.close()

# Make User model compatible with Flask-Login
User.is_authenticated = property(lambda self: True)
User.is_active = property(lambda self: True)
User.is_anonymous = property(lambda self: False)
User.get_id = lambda self: str(self.id)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, close in routes

@app.route('/')
@login_required
def dashboard():
    db = get_db()
    try:
        # Fetch data for dashboard
        orders = db.query(Order).all()
        projects = db.query(Project).all()
        suppliers = db.query(Supplier).all()
        
        # Calculate metrics
        total_orders = len(orders)
        in_transit = len([o for o in orders if o.status == "In Transit"])
        delivered = len([o for o in orders if o.status == "Delivered"])
        active_projects = len([p for p in projects if p.status == "Active"])
        
        # Order status distribution
        order_statuses = {}
        for order in orders:
            status = order.status or "Unknown"
            order_statuses[status] = order_statuses.get(status, 0) + 1
        
        # Project status distribution
        project_statuses = {}
        for project in projects:
            status = project.status or "Unknown"
            project_statuses[status] = project_statuses.get(status, 0) + 1
        
        return render_template('dashboard.html',
                             total_orders=total_orders,
                             in_transit=in_transit,
                             delivered=delivered,
                             active_projects=active_projects,
                             orders=orders[:10],  # Recent orders
                             order_statuses=order_statuses,
                             project_statuses=project_statuses)
    finally:
        db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            
            # Use the existing auth system from backend
            from backend.auth import verify_password
            if user and verify_password(password, user.hashed_password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password')
        finally:
            db.close()
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/orders')
@login_required
def orders():
    db = get_db()
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'All')
        priority_filter = request.args.get('priority', 'All')
        supplier_filter = request.args.get('supplier', 'All')
        
        # Base query
        query = db.query(Order)
        
        # Apply filters
        if status_filter != 'All':
            query = query.filter(Order.status == status_filter)
        if priority_filter != 'All':
            query = query.filter(Order.priority == priority_filter)
        if supplier_filter != 'All':
            query = query.join(Supplier).filter(Supplier.name == supplier_filter)
        
        orders = query.all()
        
        # Get unique values for filters
        all_orders = db.query(Order).all()
        statuses = list(set([o.status for o in all_orders if o.status]))
        priorities = list(set([o.priority for o in all_orders if o.priority]))
        
        suppliers = db.query(Supplier).all()
        supplier_names = [s.name for s in suppliers]
        
        return render_template('orders.html', 
                             orders=orders,
                             statuses=statuses,
                             priorities=priorities,
                             supplier_names=supplier_names,
                             current_status=status_filter,
                             current_priority=priority_filter,
                             current_supplier=supplier_filter)
    finally:
        db.close()

@app.route('/projects')
@login_required
def projects():
    db = get_db()
    try:
        projects = db.query(Project).all()
        
        # Calculate metrics
        active_projects = len([p for p in projects if p.status == "Active"])
        total_budget = sum([float(p.total_budget) for p in projects if p.total_budget])
        avg_completion = sum([p.completion_percentage for p in projects if p.completion_percentage]) / len(projects) if projects else 0
        
        return render_template('projects.html',
                             projects=projects,
                             active_projects=active_projects,
                             total_budget=total_budget,
                             avg_completion=avg_completion)
    finally:
        db.close()

@app.route('/suppliers')
@login_required
def suppliers():
    db = get_db()
    try:
        suppliers = db.query(Supplier).all()
        
        # Calculate metrics
        approved_suppliers = len([s for s in suppliers if s.approval_status == "Approved"])
        local_suppliers = len([s for s in suppliers if s.is_local_company])
        avg_performance = sum([s.overall_performance_score for s in suppliers if s.overall_performance_score]) / len(suppliers) if suppliers else 0
        
        return render_template('suppliers.html',
                             suppliers=suppliers,
                             approved_suppliers=approved_suppliers,
                             local_suppliers=local_suppliers,
                             avg_performance=avg_performance)
    finally:
        db.close()

# API endpoints for compatibility
@app.route('/api/orders')
@login_required
def api_orders():
    db = get_db()
    try:
        orders = db.query(Order).all()
        return jsonify([
            {
                "id": order.id,
                "order_number": order.order_number,
                "po_number": order.po_number,
                "description": order.description,
                "status": order.status,
                "priority": order.priority,
                "quantity": order.quantity,
                "unit_price": float(order.unit_price) if order.unit_price else 0,
                "total_amount": float(order.total_amount) if order.total_amount else 0,
                "currency": order.currency,
                "order_date": order.order_date.isoformat() if order.order_date else None,
                "requested_delivery_date": order.requested_delivery_date.isoformat() if order.requested_delivery_date else None,
                "promised_delivery_date": order.promised_delivery_date.isoformat() if order.promised_delivery_date else None,
                "actual_delivery_date": order.actual_delivery_date.isoformat() if order.actual_delivery_date else None,
                "project_name": order.project.name if order.project else None,
                "supplier_name": order.supplier.name if order.supplier else None
            }
            for order in orders
        ])
    finally:
        db.close()

@app.route('/api/projects')
@login_required
def api_projects():
    db = get_db()
    try:
        projects = db.query(Project).all()
        return jsonify([
            {
                "id": project.id,
                "name": project.name,
                "project_code": project.project_code,
                "client_name": project.client_name,
                "status": project.status,
                "priority": project.priority,
                "completion_percentage": project.completion_percentage,
                "total_budget": float(project.total_budget) if project.total_budget else None,
                "currency": project.currency,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "planned_completion_date": project.planned_completion_date.isoformat() if project.planned_completion_date else None
            }
            for project in projects
        ])
    finally:
        db.close()

@app.route('/api/suppliers')
@login_required
def api_suppliers():
    db = get_db()
    try:
        suppliers = db.query(Supplier).all()
        return jsonify([
            {
                "id": supplier.id,
                "name": supplier.name,
                "supplier_code": supplier.supplier_code,
                "primary_contact_person": supplier.primary_contact_person,
                "primary_email": supplier.primary_email,
                "country": supplier.country,
                "is_local_company": supplier.is_local_company,
                "approval_status": supplier.approval_status,
                "on_time_delivery_rate": float(supplier.on_time_delivery_rate) if supplier.on_time_delivery_rate else 0,
                "overall_performance_score": float(supplier.overall_performance_score) if supplier.overall_performance_score else 0
            }
            for supplier in suppliers
        ])
    finally:
        db.close()

if __name__ == '__main__':
    # Create default admin user
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            from backend.auth import get_password_hash
            admin_user = User(
                username="admin",
                email="s.michael@fusiongroupholding.com",
                full_name="Michael",
                hashed_password=get_password_hash("breitehose45"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()
    
    app.run(debug=True, host='0.0.0.0', port=5000)