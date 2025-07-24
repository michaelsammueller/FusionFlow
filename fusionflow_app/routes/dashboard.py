from flask import Blueprint, render_template
from flask_login import login_required, current_user
from backend.database import SessionLocal
from backend.models import User, Project, Supplier, Order, Shipment
from sqlalchemy import func, desc
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

def get_db():
    """Get database session"""
    return SessionLocal()

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page"""
    db = get_db()
    try:
        # Get key metrics
        total_orders = db.query(Order).count()
        total_projects = db.query(Project).count()
        total_suppliers = db.query(Supplier).count()
        total_shipments = db.query(Shipment).count()
        
        # Order status breakdown
        order_statuses = db.query(
            Order.status, 
            func.count(Order.id).label('count')
        ).group_by(Order.status).all()
        
        # Recent orders (last 10)
        recent_orders = db.query(Order).order_by(desc(Order.created_at)).limit(10).all()
        
        # Active projects
        active_projects = db.query(Project).filter(Project.status == 'Active').count()
        
        # Orders by priority
        priority_counts = db.query(
            Order.priority,
            func.count(Order.id).label('count')
        ).group_by(Order.priority).all()
        
        # Shipments in transit
        in_transit_shipments = db.query(Shipment).filter(
            Shipment.current_status.in_(['In Transit', 'Out for Delivery', 'Customs Delay'])
        ).count()
        
        # Recent deliveries (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_deliveries = db.query(Shipment).filter(
            Shipment.actual_delivery_date >= thirty_days_ago,
            Shipment.current_status == 'Delivered'
        ).count()
        
        # Orders requiring attention (overdue, high priority, etc.)
        attention_orders = db.query(Order).filter(
            (Order.priority == 'Critical') | 
            (Order.status == 'On Hold') |
            (Order.requested_delivery_date < datetime.utcnow())
        ).count()
        
        # Project completion stats
        project_completion = db.query(
            func.avg(Project.completion_percentage).label('avg_completion')
        ).scalar() or 0
        
        return render_template('dashboard/index.html',
                             total_orders=total_orders,
                             total_projects=total_projects,
                             total_suppliers=total_suppliers,
                             total_shipments=total_shipments,
                             active_projects=active_projects,
                             in_transit_shipments=in_transit_shipments,
                             recent_deliveries=recent_deliveries,
                             attention_orders=attention_orders,
                             project_completion=round(project_completion, 1),
                             order_statuses=order_statuses,
                             priority_counts=priority_counts,
                             recent_orders=recent_orders,
                             current_user=current_user)
    
    finally:
        db.close()