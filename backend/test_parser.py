#!/usr/bin/env python3
"""Quick test script to verify resume parser functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.resume_parser import ResumeParser

def test_parser():
    print("Testing Resume Parser...")
    
    # Initialize parser
    parser = ResumeParser()
    
    # Test spaCy loading
    if parser.nlp:
        print("✓ spaCy model loaded successfully")
        
        # Test basic NLP processing
        doc = parser.nlp("I am a software engineer with 5 years experience in Python and JavaScript.")
        print(f"✓ Processed {len(doc)} tokens")
        
        # Test skills extraction
        test_text = """
        ALEX SMITH
        Python Developer
        📧 alex.smith@email.com
        📱 +1 (555) 987-6543
        📍 San Francisco, CA
        
        PROFESSIONAL SUMMARY
        Experienced Python Developer with 3 years of expertise in building web applications and working with databases. Proficient in Git version control and API development.
        
        TECHNICAL SKILLS
        • Programming Languages: Python
        • Version Control: Git, GitHub
        • Databases: SQL, PostgreSQL, MySQL
        • Web Development: REST API, Flask, Django
        • Tools: VS Code, PyCharm
        
        PROFESSIONAL EXPERIENCE
        Python Developer | WebSolutions LLC | Jan 2021 - Present (3 years)
        • Developed Python web applications using Flask and Django frameworks
        • Built REST APIs for mobile and web applications
        • Used Git for version control and collaborative development
        
        Junior Python Developer | TechStart Inc | Jun 2020 - Dec 2020 (6 months)
        • Learned Python programming fundamentals
        • Assisted with database design and SQL queries
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of California, Berkeley | 2016-2020
        """
        
        print("\nTesting skills extraction...")
        skills = parser.extract_skills(test_text)
        print(f"Extracted skills: {skills}")
        
        print("\nTesting experience extraction...")
        experiences, total_years = parser.extract_experience(test_text)
        print(f"Total experience years: {total_years}")
        print(f"Experience entries: {len(experiences)}")
        
        print("\nTesting contact info extraction...")
        contact_info = parser.extract_contact_info(test_text)
        print(f"Contact info: {contact_info}")
        
        return True
    else:
        print("✗ spaCy model failed to load")
        return False

if __name__ == "__main__":
    success = test_parser()
    sys.exit(0 if success else 1)