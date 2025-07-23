#!/usr/bin/env python3
"""
Flask Application Runner for FusionFlow
This script initializes the database and runs the Flask application
"""
import os
import sys
from backend.database import create_tables, SessionLocal
from backend.models import User
from backend.auth import get_password_hash

def setup_database():
    """Create tables and default admin user"""
    print("Setting up database...")
    
    # Create all tables
    create_tables()
    print("✅ Database tables created")
    
    # Create default admin user
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="s.michael@fusiongroupholding.com",
                full_name="Michael",
                hashed_password=get_password_hash("breitehose45"),
                role="admin"
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

def main():
    """Main function to run the Flask app"""
    print("🚀 Starting FusionFlow Flask Application")
    print("=" * 50)
    
    # Setup database
    setup_database()
    
    print("\n🌐 Starting Flask server...")
    print("Application will be available at: http://localhost:5000")
    print("Default login: admin / breitehose45")
    print("=" * 50)
    
    # Import and run Flask app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=6000)

if __name__ == "__main__":
    main()