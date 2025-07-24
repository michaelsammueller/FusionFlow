from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.database import SessionLocal
from backend.models import Order, Project, Supplier, User
from sqlalchemy import desc, asc, func
from datetime import datetime

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

def get_db():
    """Get database session"""
    return SessionLocal()

@orders_bp.route('/')
@login_required
def list_orders():
    """List all orders with filtering and pagination"""
    db = get_db()
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        priority_filter = request.args.get('priority', 'all')
        project_filter = request.args.get('project', 'all')
        supplier_filter = request.args.get('supplier', 'all')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort', 'created_at')
        sort_order = request.args.get('order', 'desc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        
        # Build query
        query = db.query(Order)
        
        # Apply filters
        if status_filter != 'all':
            query = query.filter(Order.status == status_filter)
        if priority_filter != 'all':
            query = query.filter(Order.priority == priority_filter)
        if project_filter != 'all':
            query = query.filter(Order.project_id == int(project_filter))
        if supplier_filter != 'all':
            query = query.filter(Order.supplier_id == int(supplier_filter))
        if search:
            query = query.filter(
                (Order.order_number.contains(search)) |
                (Order.description.contains(search)) |
                (Order.po_number.contains(search))
            )
        
        # Apply sorting
        if hasattr(Order, sort_by):
            if sort_order == 'desc':
                query = query.order_by(desc(getattr(Order, sort_by)))
            else:
                query = query.order_by(asc(getattr(Order, sort_by)))
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        orders = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Get filter options
        statuses = db.query(Order.status).distinct().filter(Order.status.isnot(None)).all()
        priorities = db.query(Order.priority).distinct().filter(Order.priority.isnot(None)).all()
        projects = db.query(Project.id, Project.name).all()
        suppliers = db.query(Supplier.id, Supplier.name).all()
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('orders/list.html',
                             orders=orders,
                             total=total,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             statuses=[s[0] for s in statuses],
                             priorities=[p[0] for p in priorities],
                             projects=projects,
                             suppliers=suppliers,
                             current_filters={
                                 'status': status_filter,
                                 'priority': priority_filter,
                                 'project': project_filter,
                                 'supplier': supplier_filter,
                                 'search': search,
                                 'sort': sort_by,
                                 'order': sort_order
                             })
    finally:
        db.close()

@orders_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    """View detailed order information"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            flash('Order not found.', 'danger')
            return redirect(url_for('orders.list_orders'))
        
        return render_template('orders/detail.html', order=order)
    finally:
        db.close()

@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    """Create a new order"""
    db = get_db()
    try:
        if request.method == 'POST':
            # Get form data
            project_id = request.form.get('project_id')
            supplier_id = request.form.get('supplier_id')
            description = request.form.get('description')
            quantity = request.form.get('quantity')
            unit_price = request.form.get('unit_price')
            requested_delivery_date = request.form.get('requested_delivery_date')
            priority = request.form.get('priority', 'Normal')
            
            # Validate required fields
            if not all([project_id, supplier_id, description, quantity, unit_price, requested_delivery_date]):
                flash('Please fill in all required fields.', 'danger')
                return render_template('orders/create.html', 
                                     projects=db.query(Project).all(),
                                     suppliers=db.query(Supplier).all())
            
            try:
                # Generate order number
                last_order = db.query(Order).order_by(desc(Order.id)).first()
                order_number = f"ORD-{(last_order.id + 1 if last_order else 1):06d}"
                
                # Calculate total amount
                total_amount = float(quantity) * float(unit_price)
                
                # Create new order
                new_order = Order(
                    order_number=order_number,
                    project_id=int(project_id),
                    supplier_id=int(supplier_id),
                    created_by_id=current_user.id,
                    description=description,
                    quantity=int(quantity),
                    unit_price=float(unit_price),
                    total_amount=total_amount,
                    requested_delivery_date=datetime.strptime(requested_delivery_date, '%Y-%m-%d'),
                    priority=priority,
                    status='Draft'
                )
                
                db.add(new_order)
                db.commit()
                
                flash(f'Order {order_number} created successfully!', 'success')
                return redirect(url_for('orders.view_order', order_id=new_order.id))
                
            except ValueError as e:
                flash('Please check your input values.', 'danger')
            except Exception as e:
                flash('An error occurred while creating the order.', 'danger')
                db.rollback()
        
        # GET request - show form
        projects = db.query(Project).filter(Project.status == 'Active').all()
        suppliers = db.query(Supplier).filter(Supplier.approval_status == 'Approved').all()
        
        return render_template('orders/create.html', 
                             projects=projects, 
                             suppliers=suppliers)
    finally:
        db.close()

@orders_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    """Edit an existing order"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            flash('Order not found.', 'danger')
            return redirect(url_for('orders.list_orders'))
        
        if request.method == 'POST':
            # Update order fields
            order.description = request.form.get('description', order.description)
            order.quantity = int(request.form.get('quantity', order.quantity))
            order.unit_price = float(request.form.get('unit_price', order.unit_price))
            order.total_amount = order.quantity * order.unit_price
            order.priority = request.form.get('priority', order.priority)
            order.status = request.form.get('status', order.status)
            
            if request.form.get('requested_delivery_date'):
                order.requested_delivery_date = datetime.strptime(
                    request.form.get('requested_delivery_date'), '%Y-%m-%d'
                )
            
            try:
                db.commit()
                flash('Order updated successfully!', 'success')
                return redirect(url_for('orders.view_order', order_id=order.id))
            except Exception as e:
                flash('An error occurred while updating the order.', 'danger')
                db.rollback()
        
        return render_template('orders/edit.html', order=order)
    finally:
        db.close()

@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
def update_status(order_id):
    """Update order status via AJAX"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})
        
        new_status = request.json.get('status')
        if new_status:
            order.previous_status = order.status
            order.status = new_status
            order.status_changed_at = datetime.utcnow()
            order.status_changed_by = current_user.username
            
            db.commit()
            return jsonify({'success': True, 'message': 'Status updated successfully'})
        
        return jsonify({'success': False, 'message': 'Invalid status'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()