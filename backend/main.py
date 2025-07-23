from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, create_tables
from models.users import User
from auth import get_password_hash
import os
import dotenv

app = FastAPI(title="FusionFlow API", version="0.1.0")

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

    # Create default admin user
    db = next(get_db())
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

@app.get("/")
def read_root():
    return {"message": "FusionFlow API is running"}

@app.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    from backend.models.projects import projects
    projects = db.query(Project).all()
    return projects

@app.get("/suppliers")
def get_suppliers(db: Session = Depends(get_db)):
    from backend.models.suppliers import suppliers
    suppliers = db.query(Supplier).all()
    return suppliers

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    from backend.models.orders import orders
    orders = db.query(Order).all()
    return orders