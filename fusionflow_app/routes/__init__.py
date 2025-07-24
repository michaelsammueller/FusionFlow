# Routes package
from fusionflow_app.routes.api import api_bp
from fusionflow_app.routes.users import users_bp

def register_blueprints(app):
    app.register_blueprint(api_bp)
    app.register_blueprint(users_bp)