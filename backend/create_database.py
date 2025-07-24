#!/usr/bin/env python3
"""
FusionFlow Database Creation Script

This script creates the database and all tables for the FusionFlow 
Order & Shipment Tracking Software. It handles both SQLite (default) 
and PostgreSQL databases based on the DATABASE_URL environment variable.

Usage:
    python backend/create_database.py [--recreate] [--seed]
    
Arguments:
    --recreate: Drop existing tables and recreate them (WARNING: Data loss!)
    --seed: Insert sample data after creating tables
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Add the parent directory to the Python path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base, get_db
from backend.models import (
    User, Project, Supplier, Order, Shipment, Document, 
    Notification, SupplierPerformance, CustomsEntry, CostBreakdown
)

# Import all model classes to ensure they're registered with SQLAlchemy
from backend.models.audit_log import AuditLog
from backend.models.system_settings import SystemSettings

# Migration: add_assigned_user_id_to_projects_orders_shipments.py
import sqlalchemy as sa
from sqlalchemy import MetaData, Table, Column, Integer, ForeignKey

def migrate_add_assigned_user_id(engine):
    meta = MetaData()
    meta.reflect(bind=engine)
    for table_name in ['projects', 'orders', 'shipments']:
        table = meta.tables.get(table_name)
        if table is not None and 'assigned_user_id' not in table.c:
            with engine.connect() as conn:
                conn.execute(sa.text(f'ALTER TABLE {table_name} ADD COLUMN assigned_user_id INTEGER REFERENCES users(id)'))
    print('Migration: assigned_user_id added to projects, orders, shipments.')

def migrate_add_level_to_audit_logs(engine):
    meta = MetaData()
    meta.reflect(bind=engine)
    table = meta.tables.get('audit_logs')
    if table is not None and 'level' not in table.c:
        with engine.connect() as conn:
            conn.execute(sa.text('ALTER TABLE audit_logs ADD COLUMN level VARCHAR(20) DEFAULT "info"'))
    print('Migration: level column added to audit_logs.')

def create_database(recreate=False, seed=False):
    """
    Create the database and all tables.
    
    Args:
        recreate (bool): If True, drop existing tables and recreate them
        seed (bool): If True, insert sample data after creating tables
    """
    print("FusionFlow Database Creation Script")
    print("=" * 50)
    
    # Get database URL for informational purposes
    database_url = os.getenv("DATABASE_URL", "sqlite:///./fusionflow.db")
    db_type = "SQLite" if database_url.startswith("sqlite") else "PostgreSQL"
    
    print(f"Database Type: {db_type}")
    print(f"Database URL: {database_url}")
    print()
    
    try:
        if recreate:
            print("⚠️  WARNING: Dropping existing tables...")
            Base.metadata.drop_all(bind=engine)
            print("✅ Existing tables dropped successfully")
        
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Verify table creation
        print("\nVerifying table creation...")
        tables = Base.metadata.tables.keys()
        for table in sorted(tables):
            print(f"  ✓ {table}")
        
        print(f"\n✅ Successfully created {len(tables)} tables")
        
        if seed:
            print("\nSeeding database with sample data...")
            seed_database()
            print("✅ Sample data inserted successfully")
            
    except Exception as e:
        print(f"❌ Error creating database: {str(e)}")
        sys.exit(1)

def seed_database():
    """Insert sample data for testing and development."""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create sample users
        admin_user = User(
            email="admin@fusionflow.qa",
            username="admin",
            full_name="System Administrator",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin123
            role="admin",
            department="Management",
            is_active=True,
            created_by="system"
        )
        
        manager_user = User(
            email="manager@fusionflow.qa",
            username="manager",
            full_name="Project Manager",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin123
            role="manager",
            department="Management",
            is_active=True,
            created_by="admin"
        )
        
        procurement_user = User(
            email="procurement@fusionflow.qa",
            username="procurement",
            full_name="Procurement Specialist",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin123
            role="procurement",
            department="Procurement",
            is_active=True,
            created_by="admin"
        )
        
        db.add_all([admin_user, manager_user, procurement_user])
        db.commit()
        
        # Create sample suppliers
        local_supplier = Supplier(
            name="Qatar Aviation Services LLC",
            supplier_code="QAS001",
            primary_contact_person="Ahmed Al-Mahmoud",
            primary_email="ahmed@qas.qa",
            primary_phone="+974 4444 5555",
            address_line1="Industrial Area, Street 38",
            city="Doha",
            country="Qatar",
            is_local_company=True,
            certifications=["ISO 9001:2015", "AS9100D", "QCAA Approved"],
            product_categories=["Aviation Parts", "Ground Support Equipment"],
            geographical_coverage=["Qatar", "GCC"],
            payment_terms="30 days",
            currency_preference="QAR",
            approval_status="Approved",
            approved_by="admin",
            approval_date=datetime.utcnow(),
            created_by="admin"
        )
        
        international_supplier = Supplier(
            name="Aerospace Components International",
            supplier_code="ACI001",
            primary_contact_person="John Smith",
            primary_email="john.smith@aci-aerospace.com",
            primary_phone="+1-555-123-4567",
            address_line1="1234 Aerospace Blvd",
            city="Seattle",
            state="Washington",
            country="United States",
            is_local_company=False,
            certifications=["FAA Approved", "EASA Part 145", "ISO 9001:2015", "AS9100D"],
            product_categories=["Avionics", "Engine Components", "Navigation Systems"],
            geographical_coverage=["Global"],
            payment_terms="Letter of Credit",
            currency_preference="USD",
            approval_status="Approved",
            approved_by="admin",
            approval_date=datetime.utcnow(),
            created_by="admin"
        )
        
        db.add_all([local_supplier, international_supplier])
        db.commit()
        
        # Create sample project
        sample_project = Project(
            name="Hamad International Airport Terminal Expansion",
            project_code="HIA-TE-2024",
            client_name="Qatar Airways",
            client_contact_person="Fatima Al-Thani",
            client_email="fatima.althani@qatarairways.com",
            client_phone="+974 4023 0000",
            description="Expansion of Terminal facilities with new baggage handling systems and gate equipment",
            project_type="Aviation",
            start_date=datetime.utcnow(),
            planned_completion_date=datetime.utcnow() + timedelta(days=180),
            total_budget=Decimal("2500000.00"),
            currency="QAR",
            status="Active",
            priority="High",
            completion_percentage=25,
            project_manager_id=manager_user.id,
            created_by_id=admin_user.id,
            installation_location="Hamad International Airport",
            installation_country="Qatar",
            installation_city="Doha",
            requires_certification=True,
            certification_status="In Progress",
            regulatory_authority="QCAA"
        )
        
        db.add(sample_project)
        db.commit()
        
        # Create sample orders
        order1 = Order(
            order_number="PO-2024-001",
            po_number="HIA-PO-001",
            rfq_number="RFQ-2024-001",
            project_id=sample_project.id,
            supplier_id=local_supplier.id,
            created_by_id=procurement_user.id,
            description="Baggage conveyor belt system - 100m length with control panel",
            part_number="BCS-100M-CP",
            manufacturer_part_number="ACME-BCS-100",
            quantity=1,
            unit_of_measure="set",
            unit_price=Decimal("125000.0000"),
            total_amount=Decimal("125000.00"),
            currency="QAR",
            requested_delivery_date=datetime.utcnow() + timedelta(days=45),
            promised_delivery_date=datetime.utcnow() + timedelta(days=40),
            status="In Production",
            priority="High",
            is_critical_path=True,
            delivery_address="Hamad International Airport, Terminal Expansion Site",
            shipping_method="Road",
            incoterms="DDP",
            requires_certification=True,
            certification_type="QCAA",
            payment_terms="50% advance, 50% on delivery",
            quoted_lead_time_days=40,
            budgeted_amount=Decimal("130000.00")
        )
        
        order2 = Order(
            order_number="PO-2024-002",
            po_number="HIA-PO-002",
            project_id=sample_project.id,
            supplier_id=international_supplier.id,
            created_by_id=procurement_user.id,
            description="Advanced Navigation Display Units for Gate Control",
            part_number="NDU-GC-7000",
            manufacturer_part_number="GARMIN-NDU-7000",
            quantity=12,
            unit_of_measure="pcs",
            unit_price=Decimal("8500.0000"),
            total_amount=Decimal("102000.00"),
            currency="USD",
            exchange_rate_to_base=Decimal("3.64"),
            requested_delivery_date=datetime.utcnow() + timedelta(days=60),
            status="Confirmed",
            priority="Normal",
            delivery_address="Hamad International Airport, Terminal Expansion Site",
            shipping_method="Air",
            incoterms="CIF",
            requires_certification=True,
            certification_type="FAA/EASA",
            payment_terms="Letter of Credit",
            quoted_lead_time_days=55
        )
        
        db.add_all([order1, order2])
        db.commit()
        
        # Create sample system settings
        system_settings = [
            SystemSettings(
                setting_key="company_name",
                setting_value="FusionFlow Qatar",
                setting_type="string",
                description="Company name displayed in the application"
            ),
            SystemSettings(
                setting_key="default_currency",
                setting_value="QAR",
                setting_type="string",
                description="Default currency for new projects and orders"
            ),
            SystemSettings(
                setting_key="email_notifications_enabled",
                setting_value="true",
                setting_type="boolean",
                description="Enable email notifications for order updates"
            ),
            SystemSettings(
                setting_key="auto_backup_enabled",
                setting_value="true",
                setting_type="boolean",
                description="Enable automatic database backups"
            ),
            SystemSettings(
                setting_key="backup_retention_days",
                setting_value="30",
                setting_type="integer",
                description="Number of days to retain backup files"
            )
        ]
        
        db.add_all(system_settings)
        db.commit()
        
        print(f"  ✓ Created {len([admin_user, manager_user, procurement_user])} users")
        print(f"  ✓ Created {len([local_supplier, international_supplier])} suppliers")
        print(f"  ✓ Created 1 project")
        print(f"  ✓ Created {len([order1, order2])} orders")
        print(f"  ✓ Created {len(system_settings)} system settings")
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def main():
    """Main function to handle command line arguments and execute database creation."""
    parser = argparse.ArgumentParser(
        description="Create FusionFlow database and tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backend/create_database.py                 # Create tables only
  python backend/create_database.py --seed          # Create tables and add sample data
  python backend/create_database.py --recreate      # Drop and recreate tables
  python backend/create_database.py --recreate --seed  # Full reset with sample data
        """
    )
    
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Drop existing tables and recreate them (WARNING: This will delete all data!)"
    )
    
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Insert sample data after creating tables"
    )
    
    args = parser.parse_args()
    
    # Confirmation for recreate
    if args.recreate:
        print("⚠️  WARNING: This will delete all existing data!")
        confirm = input("Are you sure you want to continue? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            sys.exit(0)
    
    create_database(recreate=args.recreate, seed=args.seed)
    
    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the FastAPI backend: uvicorn backend.main:app --reload")
    print("2. Start the Streamlit frontend: streamlit run frontend/main.py")
    
    if args.seed:
        print("\nSample login credentials:")
        print("  Admin: admin@fusionflow.qa / admin123")
        print("  Manager: manager@fusionflow.qa / admin123")
        print("  Procurement: procurement@fusionflow.qa / admin123")

if __name__ == "__main__":
    main()