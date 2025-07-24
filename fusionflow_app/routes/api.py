from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from backend.database import SessionLocal
from backend.models import Order, Project, Supplier, Shipment, User
from sqlalchemy import func, desc
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__, url_prefix='/api')

def get_db():
    """Get database session"""
    return SessionLocal()

@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    db = get_db()
    try:
        # Key metrics
        stats = {
            'total_orders': db.query(Order).count(),
            'total_projects': db.query(Project).count(),
            'total_suppliers': db.query(Supplier).count(),
            'total_shipments': db.query(Shipment).count(),
            'active_projects': db.query(Project).filter(Project.status == 'Active').count(),
            'pending_orders': db.query(Order).filter(Order.status.in_(['Draft', 'Pending Approval'])).count(),
            'in_transit_shipments': db.query(Shipment).filter(
                Shipment.current_status.in_(['In Transit', 'Out for Delivery'])
            ).count()
        }
        
        # Order status distribution
        order_statuses = db.query(
            Order.status,
            func.count(Order.id).label('count')
        ).group_by(Order.status).all()
        
        stats['order_statuses'] = {status: count for status, count in order_statuses}
        
        # Monthly order trend (last 12 months)
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        monthly_orders = db.query(
            func.date_trunc('month', Order.created_at).label('month'),
            func.count(Order.id).label('count')
        ).filter(Order.created_at >= twelve_months_ago).group_by('month').all()
        
        stats['monthly_orders'] = [
            {'month': month.strftime('%Y-%m'), 'count': count}
            for month, count in monthly_orders
        ]
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@api_bp.route('/orders')
@login_required
def list_orders_api():
    """API endpoint for orders list"""
    db = get_db()
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)  # Max 100 per page
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        # Build query
        query = db.query(Order)
        
        if status:
            query = query.filter(Order.status == status)
        if priority:
            query = query.filter(Order.priority == priority)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        orders = query.order_by(desc(Order.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        # Format response
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'po_number': order.po_number,
                'description': order.description,
                'status': order.status,
                'priority': order.priority,
                'quantity': order.quantity,
                'unit_price': float(order.unit_price) if order.unit_price else 0,
                'total_amount': float(order.total_amount) if order.total_amount else 0,
                'currency': order.currency,
                'order_date': order.order_date.isoformat() if order.order_date else None,
                'requested_delivery_date': order.requested_delivery_date.isoformat() if order.requested_delivery_date else None,
                'project_name': order.project.name if order.project else None,
                'supplier_name': order.supplier.name if order.supplier else None,
                'created_at': order.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': orders_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@api_bp.route('/orders/<int:order_id>')
@login_required
def get_order_api(order_id):
    """API endpoint for single order details"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        order_data = {
            'id': order.id,
            'order_number': order.order_number,
            'po_number': order.po_number,
            'description': order.description,
            'status': order.status,
            'priority': order.priority,
            'quantity': order.quantity,
            'unit_price': float(order.unit_price) if order.unit_price else 0,
            'total_amount': float(order.total_amount) if order.total_amount else 0,
            'currency': order.currency,
            'order_date': order.order_date.isoformat() if order.order_date else None,
            'requested_delivery_date': order.requested_delivery_date.isoformat() if order.requested_delivery_date else None,
            'promised_delivery_date': order.promised_delivery_date.isoformat() if order.promised_delivery_date else None,
            'actual_delivery_date': order.actual_delivery_date.isoformat() if order.actual_delivery_date else None,
            'project': {
                'id': order.project.id,
                'name': order.project.name,
                'code': order.project.project_code
            } if order.project else None,
            'supplier': {
                'id': order.supplier.id,
                'name': order.supplier.name,
                'code': order.supplier.supplier_code
            } if order.supplier else None,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat()
        }
        
        return jsonify({'success': True, 'data': order_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@api_bp.route('/shipments/<int:shipment_id>/track')
@login_required
def track_shipment_api(shipment_id):
    """API endpoint for shipment tracking"""
    db = get_db()
    try:
        shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not shipment:
            return jsonify({'success': False, 'message': 'Shipment not found'}), 404
        
        tracking_data = {
            'id': shipment.id,
            'tracking_number': shipment.tracking_number,
            'carrier': shipment.carrier,
            'current_status': shipment.current_status,
            'current_location': shipment.current_location,
            'origin_address': shipment.origin_address,
            'destination_address': shipment.destination_address,
            'ship_date': shipment.ship_date.isoformat() if shipment.ship_date else None,
            'estimated_delivery_date': shipment.estimated_delivery_date.isoformat() if shipment.estimated_delivery_date else None,
            'actual_delivery_date': shipment.actual_delivery_date.isoformat() if shipment.actual_delivery_date else None,
            'last_status_update': shipment.last_status_update.isoformat() if shipment.last_status_update else None,
            'order': {
                'id': shipment.order.id,
                'order_number': shipment.order.order_number
            } if shipment.order else None
        }
        
        return jsonify({'success': True, 'data': tracking_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@api_bp.route('/projects/<int:project_id>/orders')
@login_required
def project_orders_api(project_id):
    """API endpoint for project orders"""
    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        orders = db.query(Order).filter(Order.project_id == project_id).all()
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'description': order.description,
                'status': order.status,
                'priority': order.priority,
                'total_amount': float(order.total_amount) if order.total_amount else 0,
                'currency': order.currency,
                'supplier_name': order.supplier.name if order.supplier else None,
                'created_at': order.created_at.isoformat()
            })
        
        return jsonify({'success': True, 'data': orders_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@api_bp.route('/suppliers/<int:supplier_id>/performance')
@login_required
def supplier_performance_api(supplier_id):
    """API endpoint for supplier performance metrics"""
    db = get_db()
    try:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return jsonify({'success': False, 'message': 'Supplier not found'}), 404
        
        # Get supplier orders for calculations
        orders = db.query(Order).filter(Order.supplier_id == supplier_id).all()
        
        # Calculate metrics
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.status == 'Delivered'])
        total_value = sum(order.total_amount or 0 for order in orders)
        
        # On-time delivery calculation
        delivered_orders = [o for o in orders if o.actual_delivery_date and o.requested_delivery_date]
        on_time_orders = len([o for o in delivered_orders if o.actual_delivery_date <= o.requested_delivery_date])
        on_time_rate = (on_time_orders / len(delivered_orders) * 100) if delivered_orders else 0
        
        performance_data = {
            'supplier_id': supplier.id,
            'supplier_name': supplier.name,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_value': float(total_value),
            'on_time_delivery_rate': round(on_time_rate, 2),
            'overall_rating': float(supplier.overall_performance_score) if supplier.overall_performance_score else 0,
            'quality_rating': float(supplier.quality_rating) if supplier.quality_rating else 0,
            'communication_rating': float(supplier.communication_rating) if supplier.communication_rating else 0
        }
        
        return jsonify({'success': True, 'data': performance_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()