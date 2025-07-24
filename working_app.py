#!/usr/bin/env python3
"""
Working FusionFlow Application
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from backend.database import SessionLocal, create_tables
from backend.models import User, Order, Project, Supplier, Shipment
from backend.auth import verify_password, get_password_hash

app = Flask(__name__, 
            template_folder='fusionflow_app/templates',
            static_folder='fusionflow_app/static')
app.config['SECRET_KEY'] = 'fusionflow-secret-key-2024'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    try:
        user = db.query(User).get(int(user_id))
        if user:
            user.is_authenticated = True
            user.is_active = True
            user.is_anonymous = False
            user.get_id = lambda: str(user.id)
        return user
    except:
        return None
    finally:
        db.close()

@app.route('/')
@login_required
def dashboard():
    """Dashboard page"""
    db = SessionLocal()
    try:
        # Get basic stats
        total_orders = db.query(Order).count()
        total_projects = db.query(Project).count()
        total_suppliers = db.query(Supplier).count()
        total_shipments = db.query(Shipment).count()
        
        return f"""
        <html>
        <head>
            <title>FusionFlow Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <nav class="navbar" style="background: linear-gradient(135deg, #fff 0%, #ffd700 100%); box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div class="container">
                    <div class="w-100 d-flex justify-content-between align-items-center">
                        <div style="width: 200px;"></div>
                        <h2 class="navbar-brand mx-auto mb-0" style="color: black; font-weight: 700; font-size: 1.8rem;">FusionFlow</h2>
                        <div style="width: 200px;" class="text-end">
                            <span class="text-dark me-3">Welcome, {current_user.full_name}!</span>
                            <a href="/logout" class="btn btn-outline-dark btn-sm">Logout</a>
                        </div>
                    </div>
                </div>
            </nav>
            
            <div class="container mt-4">
                <h1>📊 Dashboard</h1>
                
                <div class="row mt-4">
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3>{total_orders}</h3>
                                <p>Total Orders</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3>{total_projects}</h3>
                                <p>Projects</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3>{total_suppliers}</h3>
                                <p>Suppliers</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3>{total_shipments}</h3>
                                <p>Shipments</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="alert alert-success mt-4">
                    ✅ <strong>Flask Application is working correctly!</strong><br>
                    You are successfully logged in and can see the dashboard.
                </div>
                
                <div class="mt-4">
                    <h3>Quick Links</h3>
                    <a href="/orders" class="btn btn-primary me-2">View Orders</a>
                    <a href="/projects" class="btn btn-info me-2">View Projects</a>
                    <a href="/suppliers" class="btn btn-success me-2">View Suppliers</a>
                    <a href="/shipments" class="btn btn-warning">View Shipments</a>
                </div>
            </div>
        </body>
        </html>
        """
    finally:
        db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('auth/login_simple.html')
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            
            if user and user.is_active and verify_password(password, user.hashed_password):
                user.is_authenticated = True
                user.is_active = True
                user.is_anonymous = False
                user.get_id = lambda: str(user.id)
                
                login_user(user, remember=bool(request.form.get('remember')))
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'danger')
        finally:
            db.close()
    
    return render_template('auth/login_simple.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/orders')
@login_required
def orders():
    return "<h1>Orders Page</h1><p>Orders functionality will be here.</p><a href='/'>Back to Dashboard</a>"

@app.route('/projects')  
@login_required
def projects():
    return "<h1>Projects Page</h1><p>Projects functionality will be here.</p><a href='/'>Back to Dashboard</a>"

@app.route('/suppliers')
@login_required
def suppliers():
    return "<h1>Suppliers Page</h1><p>Suppliers functionality will be here.</p><a href='/'>Back to Dashboard</a>"

@app.route('/shipments')
@login_required
def shipments():
    return "<h1>Shipments Page</h1><p>Shipments functionality will be here.</p><a href='/'>Back to Dashboard</a>"

def setup_default_admin():
    """Create default admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@fusionflow.com",
                full_name="System Administrator",
                hashed_password=get_password_hash("breitehose45"),
                role="admin",
                department="Management",
                is_active=True,
                created_by="system"
            )
            db.add(admin_user)
            db.commit()
            print("✅ Default admin user created (admin/breitehose45)")
        else:
            print("✅ Admin user already exists")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    print("🚀 Starting FusionFlow Working Application")
    print("=" * 50)
    
    # Setup database and default user
    create_tables()
    setup_default_admin()
    
    print("\n🌐 Flask server starting...")
    print("Application URL: http://localhost:5001")
    print("Login: admin / breitehose45")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)