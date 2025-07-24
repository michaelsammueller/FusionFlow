from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.database import SessionLocal
from backend.models import Shipment, Order, ShipmentStatusHistory
from sqlalchemy import desc, asc
from datetime import datetime

shipments_bp = Blueprint('shipments', __name__, url_prefix='/shipments')

def get_db():
    """Get database session"""
    return SessionLocal()

@shipments_bp.route('/')
@login_required
def list_shipments():
    """List all shipments with filtering"""
    db = get_db()
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        carrier_filter = request.args.get('carrier', 'all')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        
        # Build query
        query = db.query(Shipment)
        
        # Apply filters
        if status_filter != 'all':
            query = query.filter(Shipment.current_status == status_filter)
        if carrier_filter != 'all':
            query = query.filter(Shipment.carrier == carrier_filter)
        if search:
            query = query.filter(
                (Shipment.tracking_number.contains(search)) |
                (Shipment.carrier.contains(search))
            )
        
        # Order by latest first
        query = query.order_by(desc(Shipment.created_at))
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        shipments = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Get filter options
        statuses = db.query(Shipment.current_status).distinct().filter(
            Shipment.current_status.isnot(None)
        ).all()
        carriers = db.query(Shipment.carrier).distinct().filter(
            Shipment.carrier.isnot(None)
        ).all()
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('shipments/list.html',
                             shipments=shipments,
                             total=total,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             statuses=[s[0] for s in statuses],
                             carriers=[c[0] for c in carriers],
                             current_filters={
                                 'status': status_filter,
                                 'carrier': carrier_filter,
                                 'search': search
                             })
    finally:
        db.close()

@shipments_bp.route('/<int:shipment_id>')
@login_required
def view_shipment(shipment_id):
    """View detailed shipment information"""
    db = get_db()
    try:
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            flash('Shipment not found.', 'danger')
            return redirect(url_for('shipments.list_shipments'))
        
        # Get status history
        status_history = db.query(ShipmentStatusHistory).filter(
            ShipmentStatusHistory.shipment_id == shipment_id
        ).order_by(desc(ShipmentStatusHistory.timestamp)).all()
        
        return render_template('shipments/detail.html', 
                             shipment=shipment, 
                             status_history=status_history)
    finally:
        db.close()

@shipments_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_shipment():
    """Create a new shipment"""
    db = get_db()
    try:
        if request.method == 'POST':
            # Get form data
            order_id = request.form.get('order_id')
            tracking_number = request.form.get('tracking_number')
            carrier = request.form.get('carrier')
            service_type = request.form.get('service_type')
            origin_address = request.form.get('origin_address')
            destination_address = request.form.get('destination_address')
            
            # Validate required fields
            if not all([order_id, tracking_number, carrier, origin_address, destination_address]):
                flash('Please fill in all required fields.', 'danger')
                return render_template('shipments/create.html',
                                     orders=db.query(Order).filter(Order.status.in_(['Approved', 'Confirmed'])).all())
            
            try:
                # Create new shipment
                new_shipment = Shipment(
                    order_id=int(order_id),
                    tracking_number=tracking_number,
                    carrier=carrier,
                    service_type=service_type,
                    origin_address=origin_address,
                    destination_address=destination_address,
                    current_status='Label Created'
                )
                
                db.add(new_shipment)
                db.commit()
                
                # Create initial status history entry
                status_entry = ShipmentStatusHistory(
                    shipment_id=new_shipment.id,
                    status='Label Created',
                    timestamp=datetime.utcnow(),
                    description='Shipment created and label generated',
                    update_source='Manual',
                    updated_by=current_user.username
                )
                
                db.add(status_entry)
                db.commit()
                
                flash(f'Shipment {tracking_number} created successfully!', 'success')
                return redirect(url_for('shipments.view_shipment', shipment_id=new_shipment.id))
                
            except Exception as e:
                flash('An error occurred while creating the shipment.', 'danger')
                db.rollback()
        
        # GET request - show form
        orders = db.query(Order).filter(Order.status.in_(['Approved', 'Confirmed'])).all()
        
        return render_template('shipments/create.html', orders=orders)
    finally:
        db.close()

@shipments_bp.route('/<int:shipment_id>/track')
@login_required
def track_shipment(shipment_id):
    """Track shipment status"""
    db = get_db()
    try:
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            return jsonify({'success': False, 'message': 'Shipment not found'})
        
        # Get latest status history
        status_history = db.query(ShipmentStatusHistory).filter(
            ShipmentStatusHistory.shipment_id == shipment_id
        ).order_by(desc(ShipmentStatusHistory.timestamp)).all()
        
        # Format response
        tracking_data = {
            'tracking_number': shipment.tracking_number,
            'carrier': shipment.carrier,
            'current_status': shipment.current_status,
            'current_location': shipment.current_location,
            'estimated_delivery': shipment.estimated_delivery_date.isoformat() if shipment.estimated_delivery_date else None,
            'status_history': [
                {
                    'status': entry.status,
                    'location': entry.location,
                    'timestamp': entry.timestamp.isoformat(),
                    'description': entry.description
                }
                for entry in status_history
            ]
        }
        
        return jsonify({'success': True, 'data': tracking_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@shipments_bp.route('/<int:shipment_id>/update-status', methods=['POST'])
@login_required
def update_shipment_status(shipment_id):
    """Update shipment status manually"""
    db = get_db()
    try:
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            return jsonify({'success': False, 'message': 'Shipment not found'})
        
        new_status = request.json.get('status')
        location = request.json.get('location', '')
        description = request.json.get('description', '')
        
        if not new_status:
            return jsonify({'success': False, 'message': 'Status is required'})
        
        # Update shipment
        shipment.current_status = new_status
        shipment.current_location = location
        shipment.last_status_update = datetime.utcnow()
        
        # If delivered, set delivery date
        if new_status == 'Delivered':
            shipment.actual_delivery_date = datetime.utcnow()
        
        # Create status history entry
        status_entry = ShipmentStatusHistory(
            shipment_id=shipment_id,
            status=new_status,
            location=location,
            timestamp=datetime.utcnow(),
            description=description,
            update_source='Manual',
            updated_by=current_user.username
        )
        
        db.add(status_entry)
        db.commit()
        
        return jsonify({'success': True, 'message': 'Status updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@shipments_bp.route('/<int:shipment_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_shipment(shipment_id):
    db = get_db()
    try:
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            flash('Shipment not found.', 'danger')
            return redirect(url_for('shipments.list_shipments'))
        confirm = request.form.get('confirm') == 'yes'
        if not confirm:
            return render_template('shipments/delete_confirm.html', shipment=shipment)
        db.delete(shipment)
        db.commit()
        flash('Shipment deleted successfully.', 'success')
        return redirect(url_for('shipments.list_shipments'))
    except Exception as e:
        db.rollback()
        flash('An error occurred while deleting the shipment.', 'danger')
        return redirect(url_for('shipments.view_shipment', shipment_id=shipment_id))
    finally:
        db.close()