"""
Script to recalculate all resume match scores with the enhanced algorithm
"""
from config.database import db
from models.resume_model import Resume
from models.job_model import JobDescription
from models.user_model import User
from services.enhanced_job_matcher import EnhancedJobMatcher
import json

def recalculate_all_scores():
    """Recalculate match scores for all resumes using enhanced algorithm"""
    try:
        # Get all resumes
        resumes = Resume.query.filter(Resume.status != 'deleted').all()
        updated_count = 0
        
        matcher = EnhancedJobMatcher()
        
        for resume in resumes:
            try:
                # Get job data
                job = resume.job
                if not job:
                    print(f"No job found for resume {resume.id}")
                    continue
                
                # Get candidate name from user relationship
                candidate = User.query.get(resume.candidate_id)
                candidate_name = candidate.name if candidate else 'Unknown'
                
                job_data = {
                    'skills_required': job.get_skills_required() or [],
                    'skills_preferred': job.get_skills_preferred() or [],
                    'extracted_skills': job.get_skills() or [],
                    'experience_required': job.experience_required or '',
                    'title': job.title
                }
                
                # Get resume data - convert from JSON string to dict
                resume_data = resume.get_parsed_data()  # This returns a dict
                
                if not resume_data:
                    print(f"No parsed data for resume {resume.id}")
                    continue
                
                # Calculate enhanced match score
                match_result = matcher.calculate_overall_match_score(resume_data, job_data)
                
                # Update the resume with new match score
                resume.match_score = match_result['overall_score']
                updated_count += 1
                
                print(f"Updated {candidate_name} for {job.title}: {match_result['overall_score']}%")
                
            except Exception as e:
                print(f"Failed to update resume {resume.id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully recalculated match scores for {updated_count} resumes")
        
    except Exception as e:
        print(f"Failed to recalculate scores: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        recalculate_all_scores()