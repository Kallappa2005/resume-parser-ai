#!/usr/bin/env python3
"""Debug script to check job skills in database"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.database import db
from models.job_model import JobDescription

def check_job_skills():
    app = create_app()
    
    with app.app_context():
        print("Checking job skills in database...")
        jobs = JobDescription.query.all()
        
        if not jobs:
            print("No jobs found in database!")
            return
            
        for job in jobs:
            print(f"\nJob: {job.title}")
            print(f"Required skills: {job.get_skills_required()}")
            print(f"Preferred skills: {job.get_skills_preferred()}")
            print(f"All skills: {job.get_skills()}")
            print(f"Skills text: {job.skills}")
            print("-" * 60)

if __name__ == "__main__":
    check_job_skills()