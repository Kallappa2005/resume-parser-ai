#!/usr/bin/env python3
"""Create database tables"""

from app import create_app
from config.database import db

def create_database():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    create_database()