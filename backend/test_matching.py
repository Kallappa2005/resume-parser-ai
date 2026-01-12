#!/usr/bin/env python3
"""Debug script to test skills matching"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_job_matcher import EnhancedJobMatcher

def test_skills_matching():
    matcher = EnhancedJobMatcher()
    
    # Test skills from the resume screenshot
    resume_skills = ['Ai', 'Css', 'Git', 'Html', 'Java', 'Javascript', 'Linux', 'Ml', 'R', 'Rest Api', 'Scala', 'Sql', 'Ui', 'Unix', 'Version Control']
    
    # Test skills from the job
    job_required = ['Java', 'Unix']
    job_preferred = ['git', 'HTML/CSS']
    
    print("=== Skills Matching Test ===")
    print(f"Resume skills: {resume_skills}")
    print(f"Job required: {job_required}")
    print(f"Job preferred: {job_preferred}")
    print()
    
    # Test individual skill similarities
    print("=== Individual Skill Similarities ===")
    for job_skill in job_required + job_preferred:
        print(f"\nJob skill: '{job_skill}'")
        for resume_skill in resume_skills:
            similarity = matcher.calculate_skills_similarity(job_skill, resume_skill)
            if similarity > 0.5:  # Only show meaningful matches
                print(f"  vs '{resume_skill}': {similarity:.3f}")
    
    print("\n" + "="*60)
    
    # Test full matching
    result = matcher.calculate_skills_match(
        resume_skills, 
        job_required + job_preferred,
        job_required,
        job_preferred
    )
    
    print("=== Full Matching Results ===")
    print(f"Overall score: {result['overall']}%")
    print(f"Required score: {result['required']}%") 
    print(f"Preferred score: {result['preferred']}%")
    print(f"Matched skills: {len(result.get('matched_skills', []))}")
    
    for match in result.get('matched_skills', []):
        print(f"  {match['type']}: '{match['job_skill']}' -> '{match['resume_skill']}' ({match['similarity']:.3f})")

if __name__ == "__main__":
    test_skills_matching()