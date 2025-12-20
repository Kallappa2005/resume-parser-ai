from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
    """Initialize database and create all tables"""
    from models.user_model import User
    from models.job_model import JobDescription
    from models.resume_model import Resume
    
    db.create_all()
    print("Database initialized successfully!")