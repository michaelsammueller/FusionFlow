from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from backend.database import SessionLocal
from backend.models import User
from backend.auth import verify_password

auth_bp = Blueprint('auth', __name__)

def get_db():
    """Get database session"""
    return SessionLocal()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('auth/login.html')
        
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            
            if user and user.is_active and verify_password(password, user.hashed_password):
                # Make user compatible with Flask-Login
                user.is_authenticated = True
                user.is_active = True
                user.is_anonymous = False
                user.get_id = lambda: str(user.id)
                
                login_user(user, remember=remember)
                
                # Update last login
                from datetime import datetime
                user.last_login = datetime.utcnow()
                db.commit()
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid username or password.', 'danger')
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'danger')
        finally:
            db.close()
    
    return render_template('auth/login_simple.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)