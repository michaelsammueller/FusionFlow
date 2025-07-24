from flask import Flask
from flask_login import LoginManager
import os

login_manager = LoginManager()

def create_app():
    """Flask application factory for FusionFlow SaaS"""
    app = Flask(__name__, 
                static_folder='static', 
                template_folder='templates')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fusionflow-saas-secret-key-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///./fusionflow.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from backend.database import SessionLocal
        from backend.models import User
        db = SessionLocal()
        try:
            user = db.query(User).get(int(user_id))
            if user:
                # Make User model compatible with Flask-Login
                user.is_authenticated = True
                user.is_active = True
                user.is_anonymous = False
                user.get_id = lambda: str(user.id)
            return user
        except:
            return None
        finally:
            db.close()
    
    # Register blueprints
    from fusionflow_app.routes.auth import auth_bp
    from fusionflow_app.routes.dashboard import dashboard_bp
    from fusionflow_app.routes.orders import orders_bp
    from fusionflow_app.routes.shipments import shipments_bp
    from fusionflow_app.routes.projects import projects_bp
    from fusionflow_app.routes.suppliers import suppliers_bp
    from fusionflow_app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(shipments_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(api_bp)
    
    # Add a simple test route to debug
    @app.route('/test')
    def test():
        return '<h1>Flask is working!</h1><a href="/login">Go to Login</a>'
    
    # Database initialization
    with app.app_context():
        from backend.database import create_tables
        create_tables()
    
    return app