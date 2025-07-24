from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from backend.database import SessionLocal
from backend.models import Project, Order, User
from sqlalchemy import desc, func
from datetime import datetime

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

def get_db():
    """Get database session"""
    return SessionLocal()

@projects_bp.route('/')
@login_required
def list_projects():
    """List all projects with filtering"""
    db = get_db()
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        priority_filter = request.args.get('priority', 'all')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        
        # Build query
        query = db.query(Project)
        
        # Apply filters
        if status_filter != 'all':
            query = query.filter(Project.status == status_filter)
        if priority_filter != 'all':
            query = query.filter(Project.priority == priority_filter)
        if search:
            query = query.filter(
                (Project.name.contains(search)) |
                (Project.project_code.contains(search)) |
                (Project.client_name.contains(search))
            )
        
        # Order by latest first
        query = query.order_by(desc(Project.created_at))
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        projects = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Get filter options
        statuses = db.query(Project.status).distinct().filter(Project.status.isnot(None)).all()
        priorities = db.query(Project.priority).distinct().filter(Project.priority.isnot(None)).all()
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('projects/list.html',
                             projects=projects,
                             total=total,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             statuses=[s[0] for s in statuses],
                             priorities=[p[0] for p in priorities],
                             current_filters={
                                 'status': status_filter,
                                 'priority': priority_filter,
                                 'search': search
                             })
    finally:
        db.close()

@projects_bp.route('/<int:project_id>')
@login_required
def view_project(project_id):
    """View detailed project information"""
    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            flash('Project not found.', 'danger')
            return redirect(url_for('projects.list_projects'))
        
        # Get project orders
        orders = db.query(Order).filter(Order.project_id == project_id).all()
        
        # Calculate project metrics
        total_orders = len(orders)
        total_order_value = sum(order.total_amount or 0 for order in orders)
        completed_orders = len([o for o in orders if o.status == 'Delivered'])
        pending_orders = len([o for o in orders if o.status in ['Draft', 'Pending Approval', 'Approved']])
        
        return render_template('projects/detail.html',
                             project=project,
                             orders=orders,
                             total_orders=total_orders,
                             total_order_value=total_order_value,
                             completed_orders=completed_orders,
                             pending_orders=pending_orders)
    finally:
        db.close()

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    """Create a new project"""
    db = get_db()
    try:
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            client_name = request.form.get('client_name')
            description = request.form.get('description')
            project_type = request.form.get('project_type')
            start_date = request.form.get('start_date')
            planned_completion_date = request.form.get('planned_completion_date')
            total_budget = request.form.get('total_budget')
            priority = request.form.get('priority', 'Normal')
            status = request.form.get('status', 'Planning')
            
            # Validate required fields
            if not all([name, client_name, start_date, planned_completion_date]):
                flash('Please fill in all required fields.', 'danger')
                return render_template('projects/create.html')
            
            try:
                # Generate project code
                last_project = db.query(Project).order_by(desc(Project.id)).first()
                project_code = f"PRJ-{(last_project.id + 1 if last_project else 1):04d}"
                
                # Create new project
                new_project = Project(
                    name=name,
                    project_code=project_code,
                    client_name=client_name,
                    description=description,
                    project_type=project_type,
                    start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                    planned_completion_date=datetime.strptime(planned_completion_date, '%Y-%m-%d'),
                    total_budget=float(total_budget) if total_budget else None,
                    priority=priority,
                    status=status,
                    created_by_id=current_user.id,
                    project_manager_id=current_user.id
                )
                
                db.add(new_project)
                db.commit()
                
                flash(f'Project {project_code} created successfully!', 'success')
                return redirect(url_for('projects.view_project', project_id=new_project.id))
                
            except ValueError as e:
                flash('Please check your input values.', 'danger')
            except Exception as e:
                flash('An error occurred while creating the project.', 'danger')
                db.rollback()
        
        return render_template('projects/create.html')
    finally:
        db.close()

@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edit an existing project"""
    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            flash('Project not found.', 'danger')
            return redirect(url_for('projects.list_projects'))
        
        if request.method == 'POST':
            # Update project fields
            project.name = request.form.get('name', project.name)
            project.client_name = request.form.get('client_name', project.client_name)
            project.description = request.form.get('description', project.description)
            project.project_type = request.form.get('project_type', project.project_type)
            project.priority = request.form.get('priority', project.priority)
            project.status = request.form.get('status', project.status)
            project.completion_percentage = int(request.form.get('completion_percentage', project.completion_percentage or 0))
            
            if request.form.get('total_budget'):
                project.total_budget = float(request.form.get('total_budget'))
            
            if request.form.get('planned_completion_date'):
                project.planned_completion_date = datetime.strptime(
                    request.form.get('planned_completion_date'), '%Y-%m-%d'
                )
            
            try:
                db.commit()
                flash('Project updated successfully!', 'success')
                return redirect(url_for('projects.view_project', project_id=project.id))
            except Exception as e:
                flash('An error occurred while updating the project.', 'danger')
                db.rollback()
        
        return render_template('projects/edit.html', project=project)
    finally:
        db.close()

@projects_bp.route('/<int:project_id>/progress', methods=['POST'])
@login_required
def update_progress(project_id):
    """Update project progress via AJAX"""
    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return jsonify({'success': False, 'message': 'Project not found'})
        
        progress = request.json.get('progress')
        if progress is not None and 0 <= progress <= 100:
            project.completion_percentage = progress
            
            # Auto-update status based on progress
            if progress == 0:
                project.status = 'Planning'
            elif progress == 100:
                project.status = 'Completed'
                project.actual_completion_date = datetime.utcnow()
            elif progress > 0:
                project.status = 'Active'
            
            db.commit()
            return jsonify({'success': True, 'message': 'Progress updated successfully'})
        
        return jsonify({'success': False, 'message': 'Invalid progress value'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@projects_bp.route('/<int:project_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_project(project_id):
    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            flash('Project not found.', 'danger')
            return redirect(url_for('projects.list_projects'))
        confirm = request.form.get('confirm') == 'yes'
        if not confirm:
            return render_template('projects/delete_confirm.html', project=project)
        db.delete(project)
        db.commit()
        flash('Project deleted successfully.', 'success')
        return redirect(url_for('projects.list_projects'))
    except Exception as e:
        db.rollback()
        flash('An error occurred while deleting the project.', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))
    finally:
        db.close()