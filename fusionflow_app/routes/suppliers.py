from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.database import SessionLocal
from backend.models import Supplier, Order, SupplierPerformance
from sqlalchemy import desc, func
from datetime import datetime

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

def get_db():
    """Get database session"""
    return SessionLocal()

@suppliers_bp.route('/')
@login_required
def list_suppliers():
    """List all suppliers with filtering"""
    db = get_db()
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        country_filter = request.args.get('country', 'all')
        local_filter = request.args.get('local', 'all')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        
        # Build query
        query = db.query(Supplier)
        
        # Apply filters
        if status_filter != 'all':
            query = query.filter(Supplier.approval_status == status_filter)
        if country_filter != 'all':
            query = query.filter(Supplier.country == country_filter)
        if local_filter == 'yes':
            query = query.filter(Supplier.is_local_company == True)
        elif local_filter == 'no':
            query = query.filter(Supplier.is_local_company == False)
        if search:
            query = query.filter(
                (Supplier.name.contains(search)) |
                (Supplier.supplier_code.contains(search)) |
                (Supplier.primary_contact_person.contains(search))
            )
        
        # Order by name
        query = query.order_by(Supplier.name)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        suppliers = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Get filter options
        statuses = db.query(Supplier.approval_status).distinct().filter(
            Supplier.approval_status.isnot(None)
        ).all()
        countries = db.query(Supplier.country).distinct().filter(
            Supplier.country.isnot(None)
        ).all()
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('suppliers/list.html',
                             suppliers=suppliers,
                             total=total,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             statuses=[s[0] for s in statuses],
                             countries=[c[0] for c in countries],
                             current_filters={
                                 'status': status_filter,
                                 'country': country_filter,
                                 'local': local_filter,
                                 'search': search
                             })
    finally:
        db.close()

@suppliers_bp.route('/<int:supplier_id>')
@login_required
def view_supplier(supplier_id):
    """View detailed supplier information"""
    db = get_db()
    try:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            flash('Supplier not found.', 'danger')
            return redirect(url_for('suppliers.list_suppliers'))
        
        # Get supplier orders
        orders = db.query(Order).filter(Order.supplier_id == supplier_id).all()
        
        # Calculate performance metrics
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.status == 'Delivered'])
        total_value = sum(order.total_amount or 0 for order in orders)
        
        # On-time delivery calculation
        delivered_orders = [o for o in orders if o.actual_delivery_date and o.requested_delivery_date]
        on_time_orders = len([o for o in delivered_orders if o.actual_delivery_date <= o.requested_delivery_date])
        on_time_rate = (on_time_orders / len(delivered_orders) * 100) if delivered_orders else 0
        
        return render_template('suppliers/detail.html',
                             supplier=supplier,
                             orders=orders[:10],  # Show recent 10 orders
                             total_orders=total_orders,
                             completed_orders=completed_orders,
                             total_value=total_value,
                             on_time_rate=round(on_time_rate, 1))
    finally:
        db.close()

@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_supplier():
    """Create a new supplier"""
    db = get_db()
    try:
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            primary_contact_person = request.form.get('primary_contact_person')
            primary_email = request.form.get('primary_email')
            primary_phone = request.form.get('primary_phone')
            country = request.form.get('country')
            address_line1 = request.form.get('address_line1')
            city = request.form.get('city')
            is_local_company = bool(request.form.get('is_local_company'))
            
            # Validate required fields
            if not all([name, primary_contact_person, primary_email, country]):
                flash('Please fill in all required fields.', 'danger')
                return render_template('suppliers/create.html')
            
            try:
                # Generate supplier code
                last_supplier = db.query(Supplier).order_by(desc(Supplier.id)).first()
                supplier_code = f"SUP-{(last_supplier.id + 1 if last_supplier else 1):04d}"
                
                # Create new supplier
                new_supplier = Supplier(
                    name=name,
                    supplier_code=supplier_code,
                    primary_contact_person=primary_contact_person,
                    primary_email=primary_email,
                    primary_phone=primary_phone,
                    country=country,
                    address_line1=address_line1,
                    city=city,
                    is_local_company=is_local_company,
                    approval_status='Pending',
                    created_by=current_user.username
                )
                
                db.add(new_supplier)
                db.commit()
                
                flash(f'Supplier {supplier_code} created successfully!', 'success')
                return redirect(url_for('suppliers.view_supplier', supplier_id=new_supplier.id))
                
            except Exception as e:
                flash('An error occurred while creating the supplier.', 'danger')
                db.rollback()
        
        return render_template('suppliers/create.html')
    finally:
        db.close()

@suppliers_bp.route('/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    """Edit an existing supplier"""
    db = get_db()
    try:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            flash('Supplier not found.', 'danger')
            return redirect(url_for('suppliers.list_suppliers'))
        
        if request.method == 'POST':
            # Update supplier fields
            supplier.name = request.form.get('name', supplier.name)
            supplier.primary_contact_person = request.form.get('primary_contact_person', supplier.primary_contact_person)
            supplier.primary_email = request.form.get('primary_email', supplier.primary_email)
            supplier.primary_phone = request.form.get('primary_phone', supplier.primary_phone)
            supplier.country = request.form.get('country', supplier.country)
            supplier.address_line1 = request.form.get('address_line1', supplier.address_line1)
            supplier.city = request.form.get('city', supplier.city)
            supplier.is_local_company = bool(request.form.get('is_local_company'))
            supplier.approval_status = request.form.get('approval_status', supplier.approval_status)
            
            try:
                db.commit()
                flash('Supplier updated successfully!', 'success')
                return redirect(url_for('suppliers.view_supplier', supplier_id=supplier.id))
            except Exception as e:
                flash('An error occurred while updating the supplier.', 'danger')
                db.rollback()
        
        return render_template('suppliers/edit.html', supplier=supplier)
    finally:
        db.close()

@suppliers_bp.route('/<int:supplier_id>/approve', methods=['POST'])
@login_required
def approve_supplier(supplier_id):
    """Approve or reject a supplier"""
    db = get_db()
    try:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return jsonify({'success': False, 'message': 'Supplier not found'})
        
        action = request.json.get('action')  # 'approve' or 'reject'
        notes = request.json.get('notes', '')
        
        if action == 'approve':
            supplier.approval_status = 'Approved'
        elif action == 'reject':
            supplier.approval_status = 'Rejected'
        else:
            return jsonify({'success': False, 'message': 'Invalid action'})
        
        supplier.approved_by = current_user.username
        supplier.approval_date = datetime.utcnow()
        supplier.approval_notes = notes
        
        db.commit()
        return jsonify({'success': True, 'message': f'Supplier {action}d successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@suppliers_bp.route('/performance')
@login_required
def supplier_performance():
    """View supplier performance dashboard"""
    db = get_db()
    try:
        # Get top performing suppliers
        top_suppliers = db.query(Supplier).filter(
            Supplier.approval_status == 'Approved'
        ).order_by(desc(Supplier.overall_performance_score)).limit(10).all()
        
        # Get suppliers needing attention (low performance)
        attention_suppliers = db.query(Supplier).filter(
            Supplier.approval_status == 'Approved',
            Supplier.overall_performance_score < 3.0
        ).all()
        
        return render_template('suppliers/performance.html',
                             top_suppliers=top_suppliers,
                             attention_suppliers=attention_suppliers)
    finally:
        db.close()