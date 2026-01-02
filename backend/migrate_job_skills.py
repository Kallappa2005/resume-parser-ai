"""
Database migration script to add skills_preferred column and update existing data
"""
from config.database import db
from models.job_model import JobDescription
from sqlalchemy import text

def upgrade_job_model():
    """Add skills_preferred column to existing database"""
    try:
        # Check if column already exists
        with db.engine.connect() as connection:
            result = connection.execute(text("PRAGMA table_info(job_descriptions)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'skills_preferred' not in columns:
                # Add the new column (SQLite doesn't support IF NOT EXISTS for ADD COLUMN)
                connection.execute(text("ALTER TABLE job_descriptions ADD COLUMN skills_preferred TEXT"))
                connection.commit()
                print("Successfully added skills_preferred column")
            else:
                print("skills_preferred column already exists")
        
        # Update existing jobs to split skills between required and preferred
        jobs = JobDescription.query.all()
        for job in jobs:
            existing_skills = job.get_skills_required()
            if existing_skills and not job.skills_preferred:
                # Split existing skills: 60% required, 40% preferred
                split_point = max(1, len(existing_skills) * 60 // 100)
                required = existing_skills[:split_point]
                preferred = existing_skills[split_point:]
                
                job.set_skills_required(required)
                job.set_skills_preferred(preferred)
                print(f"Updated job {job.title}: {len(required)} required, {len(preferred)} preferred skills")
        
        db.session.commit()
        print(f"Successfully updated {len(jobs)} existing jobs")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.session.rollback()

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        upgrade_job_model()