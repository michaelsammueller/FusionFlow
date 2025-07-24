#!/usr/bin/env python3
"""
FusionFlow SaaS Application
Order & Shipment Tracking Platform
"""

from fusionflow_app import create_app
from backend.database import SessionLocal, create_tables
from backend.models import User
from backend.auth import get_password_hash

# Create Flask app using application factory
app = create_app()

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
            return True
        else:
            print("✅ Admin user already exists")
            return False
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    print("🚀 Starting FusionFlow Order & Shipment Tracking Platform")
    print("=" * 60)
    
    # Setup database and default user
    print("Setting up database...")
    create_tables()
    setup_default_admin()
    
    print("\n🌐 Starting Flask server...")
    print("Application will be available at: http://localhost:5001")
    print("Default login: admin / breitehose45")
    print("=" * 60)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5001)