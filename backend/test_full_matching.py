#!/usr/bin/env python3
"""Debug script to test the complete matching flow like in resume upload"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.database import db
from models.job_model import JobDescription
from services.enhanced_job_matcher import EnhancedJobMatcher

def test_full_matching_flow():
    app = create_app()
    
    with app.app_context():
        print("=== Testing Full Matching Flow (like in resume upload) ===")
        
        # Get the first job
        job = JobDescription.query.first()
        if not job:
            print("No jobs found!")
            return
            
        print(f"Testing with job: {job.title}")
        
        # Create job_data exactly like in resume upload
        job_data = {
            'skills_required': job.get_skills_required() or [],
            'skills_preferred': job.get_skills_preferred() or [],
            'extracted_skills': job.get_skills() or [],
            'experience_required': job.experience_required or '',
            'requirements': job.requirements or '',
            'description_text': job.description_text or ''
        }
        
        print(f"Job data skills_required: {job_data['skills_required']}")
        print(f"Job data skills_preferred: {job_data['skills_preferred']}")
        print(f"Job data extracted_skills: {job_data['extracted_skills']}")
        
        # Sample parsed resume data (like what we expect from a good resume)
        parsed_resume = {
            'skills': ['Ai', 'Css', 'Git', 'Html', 'Java', 'Javascript', 'Linux', 'Ml', 'R', 'Rest Api', 'Scala', 'Sql', 'Ui', 'Unix', 'Version Control'],
            'experience': [],
            'education': [{'degree': 'Bachelor of Technology in Computer Science', 'institution': 'University', 'year': '2021-2025'}],
            'total_experience_years': 4,
            'contact_info': {'email': 'test@example.com'}
        }
        
        # Test with EnhancedJobMatcher (what should be used)
        enhanced_matcher = EnhancedJobMatcher()
        match_result = enhanced_matcher.calculate_overall_match_score(parsed_resume, job_data)
        
        print(f"\n=== Enhanced Matcher Results ===")
        print(f"Overall score: {match_result.get('overall_score', 0)}%")
        print(f"Skills score: {match_result.get('skills', {}).get('overall', 0)}%")
        print(f"Experience score: {match_result.get('experience', {}).get('score', 0)}%")
        print(f"Education score: {match_result.get('education', {}).get('score', 0)}%")

if __name__ == "__main__":
    test_full_matching_flow()