"""
Database migration script to add job analytics fields
"""
from config.database import db
from models.job_model import JobDescription
from sqlalchemy import text

def upgrade_job_analytics():
    """Add analytics fields to existing database"""
    try:
        # Check if columns already exist and add them if needed
        with db.engine.connect() as connection:
            # Check existing columns
            result = connection.execute(text("PRAGMA table_info(job_descriptions)"))
            columns = [row[1] for row in result.fetchall()]
            
            # Add updated_at column
            if 'updated_at' not in columns:
                connection.execute(text("ALTER TABLE job_descriptions ADD COLUMN updated_at DATETIME"))
                print("Added updated_at column")
            else:
                print("updated_at column already exists")
            
            # Add view_count column
            if 'view_count' not in columns:
                connection.execute(text("ALTER TABLE job_descriptions ADD COLUMN view_count INTEGER DEFAULT 0"))
                print("Added view_count column")
            else:
                print("view_count column already exists")
            
            # Add archived_at column
            if 'archived_at' not in columns:
                connection.execute(text("ALTER TABLE job_descriptions ADD COLUMN archived_at DATETIME"))
                print("Added archived_at column")
            else:
                print("archived_at column already exists")
            
            connection.commit()
        
        # Update existing jobs with default values
        jobs = JobDescription.query.all()
        for job in jobs:
            if not hasattr(job, 'updated_at') or job.updated_at is None:
                job.updated_at = job.created_at
            if not hasattr(job, 'view_count') or job.view_count is None:
                job.view_count = 0
        
        db.session.commit()
        print(f"Successfully updated {len(jobs)} existing jobs with default analytics values")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.session.rollback()

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        upgrade_job_analytics()