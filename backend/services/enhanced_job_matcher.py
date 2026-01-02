import re
import spacy
import json
from typing import Dict, List, Set, Tuple, Optional
from difflib import SequenceMatcher
import logging

class EnhancedJobMatcher:
    """Enhanced job matching algorithm with sophisticated scoring"""
    
    def __init__(self):
        self.nlp = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logging.warning("spaCy model not loaded. Some features may be limited.")
            
        # Skill synonyms and aliases for better matching
        self.skill_synonyms = {
            'javascript': ['js', 'node.js', 'nodejs'],
            'react': ['reactjs', 'react.js'],
            'angular': ['angularjs'],
            'python': ['py'],
            'c++': ['cpp', 'cplusplus'],
            'c#': ['csharp', 'c sharp'],
            'sql': ['mysql', 'postgresql', 'sqlite'],
            'html': ['html5'],
            'css': ['css3'],
            'machine learning': ['ml', 'artificial intelligence', 'ai'],
            'docker': ['containerization'],
            'kubernetes': ['k8s'],
            'amazon web services': ['aws'],
            'google cloud': ['gcp'],
            'microsoft azure': ['azure'],
        }
        
        # Experience level mappings
        self.experience_levels = {
            'junior': (0, 2),
            'entry': (0, 1),
            'mid': (2, 5),
            'senior': (5, 10),
            'lead': (7, 15),
            'principal': (10, 20)
        }
    
    def normalize_skill(self, skill: str) -> Set[str]:
        """Normalize skill name and return all possible variations"""
        skill_lower = skill.lower().strip()
        variations = {skill_lower}
        
        # Add synonyms
        for main_skill, synonyms in self.skill_synonyms.items():
            if skill_lower == main_skill:
                variations.update(synonyms)
            elif skill_lower in synonyms:
                variations.add(main_skill)
                variations.update(synonyms)
        
        return variations
    
    def calculate_skills_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate semantic similarity between two skills"""
        # Exact match
        if skill1.lower() == skill2.lower():
            return 1.0
            
        # Check synonyms
        skill1_variants = self.normalize_skill(skill1)
        skill2_variants = self.normalize_skill(skill2)
        
        if skill1_variants & skill2_variants:
            return 1.0
            
        # Substring matching for compound skills
        if skill1.lower() in skill2.lower() or skill2.lower() in skill1.lower():
            return 0.8
            
        # String similarity
        similarity = SequenceMatcher(None, skill1.lower(), skill2.lower()).ratio()
        return similarity if similarity > 0.7 else 0.0
    
    def calculate_skills_match(self, resume_skills: List[str], job_skills: List[str], 
                             required_skills: List[str] = None, preferred_skills: List[str] = None) -> Dict[str, float]:
        """Enhanced skills matching with required/preferred distinction"""
        if not job_skills:
            return {'overall': 0.0, 'required': 0.0, 'preferred': 0.0, 'matched_skills': []}
        
        # If required/preferred not specified, treat all job skills as required
        if not required_skills and not preferred_skills:
            required_skills = job_skills
            preferred_skills = []
        elif not required_skills:
            required_skills = []
        elif not preferred_skills:
            preferred_skills = []
            
        matched_skills = []
        required_matches = 0
        preferred_matches = 0
        
        # Match required skills
        for req_skill in required_skills:
            best_match = 0.0
            best_match_skill = None
            
            for resume_skill in resume_skills:
                similarity = self.calculate_skills_similarity(req_skill, resume_skill)
                if similarity > best_match:
                    best_match = similarity
                    best_match_skill = resume_skill
            
            if best_match >= 0.8:  # Strong match threshold
                required_matches += best_match
                matched_skills.append({
                    'job_skill': req_skill,
                    'resume_skill': best_match_skill,
                    'similarity': best_match,
                    'type': 'required'
                })
        
        # Match preferred skills
        for pref_skill in preferred_skills:
            best_match = 0.0
            best_match_skill = None
            
            for resume_skill in resume_skills:
                similarity = self.calculate_skills_similarity(pref_skill, resume_skill)
                if similarity > best_match:
                    best_match = similarity
                    best_match_skill = resume_skill
            
            if best_match >= 0.8:
                preferred_matches += best_match
                matched_skills.append({
                    'job_skill': pref_skill,
                    'resume_skill': best_match_skill,
                    'similarity': best_match,
                    'type': 'preferred'
                })
        
        # Calculate scores
        required_score = (required_matches / len(required_skills) * 100) if required_skills else 100.0
        preferred_score = (preferred_matches / len(preferred_skills) * 100) if preferred_skills else 100.0
        
        # Overall score weighted by required (80%) and preferred (20%)
        overall_score = (required_score * 0.8) + (preferred_score * 0.2)
        
        return {
            'overall': round(overall_score, 2),
            'required': round(required_score, 2),
            'preferred': round(preferred_score, 2),
            'matched_skills': matched_skills
        }
    
    def extract_experience_requirements(self, requirement_text: str) -> Dict[str, int]:
        """Extract experience requirements from job description text"""
        if not requirement_text:
            return {'min_years': 0, 'max_years': 20, 'level': 'any'}
        
        req_lower = requirement_text.lower()
        
        # Extract numeric years
        year_patterns = [
            r'(\d+)[-\s]*(\d*)\s*(?:to\s*)?(?:\d*\s*)?\+?\s*years?',
            r'minimum\s*(\d+)\s*years?',
            r'at least\s*(\d+)\s*years?',
            r'(\d+)\+\s*years?'
        ]
        
        min_years = 0
        max_years = 20
        
        for pattern in year_patterns:
            matches = re.findall(pattern, req_lower)
            if matches:
                if isinstance(matches[0], tuple):
                    min_years = int(matches[0][0])
                    if matches[0][1]:
                        max_years = int(matches[0][1])
                    else:
                        max_years = min_years + 3
                else:
                    min_years = int(matches[0])
                    max_years = min_years + 3
                break
        
        # Extract experience level keywords
        level = 'any'
        for exp_level, (level_min, level_max) in self.experience_levels.items():
            if exp_level in req_lower:
                level = exp_level
                if min_years == 0:  # If no specific years mentioned, use level defaults
                    min_years = level_min
                    max_years = level_max
                break
        
        return {
            'min_years': min_years,
            'max_years': max_years,
            'level': level
        }
    
    def calculate_experience_match(self, resume_experience: Dict, job_requirements: str) -> Dict[str, float]:
        """Enhanced experience matching"""
        req_info = self.extract_experience_requirements(job_requirements)
        resume_years = resume_experience.get('total_experience_years', 0)
        
        min_required = req_info['min_years']
        max_required = req_info['max_years']
        
        # Perfect match zone
        if min_required <= resume_years <= max_required:
            score = 100.0
        # Slightly over-qualified (still good)
        elif resume_years <= max_required + 3:
            score = 90.0
        # Under-qualified but close
        elif resume_years >= min_required - 1:
            score = 75.0
        # Significantly over-qualified
        elif resume_years > max_required + 5:
            score = 70.0
        # Under-qualified
        elif resume_years >= min_required - 2:
            score = 50.0
        else:
            score = 25.0
        
        return {
            'score': score,
            'resume_years': resume_years,
            'required_min': min_required,
            'required_max': max_required,
            'level_match': req_info['level']
        }
    
    def calculate_education_match(self, resume_education: List[Dict], job_requirements: str) -> Dict[str, float]:
        """Calculate education matching score"""
        if not resume_education:
            return {'score': 50.0, 'details': 'No education information found'}
        
        req_lower = job_requirements.lower() if job_requirements else ''
        
        # Education level scoring
        education_scores = {
            'phd': 100, 'doctorate': 100,
            'master': 90, 'mba': 90,
            'bachelor': 80, 'degree': 80,
            'associate': 60,
            'diploma': 50, 'certificate': 50,
            'high school': 30
        }
        
        max_score = 0
        matched_education = None
        
        for edu in resume_education:
            edu_level = edu.get('level', '').lower()
            edu_field = edu.get('field', '').lower()
            
            # Check for education level match
            for req_ed, score in education_scores.items():
                if req_ed in req_lower and req_ed in edu_level:
                    if score > max_score:
                        max_score = score
                        matched_education = edu
                        break
        
        # If no specific requirement found, give moderate score based on highest education
        if max_score == 0:
            for edu in resume_education:
                edu_level = edu.get('level', '').lower()
                for ed_level, score in education_scores.items():
                    if ed_level in edu_level and score > max_score:
                        max_score = score
                        matched_education = edu
        
        # Default score if no education level detected
        if max_score == 0:
            max_score = 60.0
        
        return {
            'score': max_score,
            'matched_education': matched_education,
            'details': f"Matched: {matched_education.get('level', 'Unknown') if matched_education else 'General education'}"
        }
    
    def calculate_overall_match_score(self, parsed_resume: Dict, job_data: Dict) -> Dict[str, any]:
        """Calculate comprehensive match score with detailed breakdown"""
        try:
            # Extract job requirements with proper fallback logic
            required_skills = job_data.get('skills_required', [])
            preferred_skills = job_data.get('skills_preferred', [])
            all_skills = job_data.get('extracted_skills', [])
            
            # If no specific required/preferred split, use extracted skills intelligently
            if not required_skills and not preferred_skills and all_skills:
                # Split skills: first 60% as required, rest as preferred
                split_point = max(1, len(all_skills) * 60 // 100)
                required_skills = all_skills[:split_point]
                preferred_skills = all_skills[split_point:]
            elif not required_skills and not preferred_skills:
                # Fallback to any available skills
                required_skills = all_skills
                preferred_skills = []
            
            # Skills matching (60% weight)
            skills_result = self.calculate_skills_match(
                parsed_resume.get('skills', []),
                required_skills + preferred_skills,  # All skills for context
                required_skills,
                preferred_skills
            )
            
            # Experience matching (30% weight)
            experience_result = self.calculate_experience_match(
                parsed_resume,
                job_data.get('experience_required', '')
            )
            
            # Education matching (10% weight)
            education_result = self.calculate_education_match(
                parsed_resume.get('education', []),
                job_data.get('requirements', '') + ' ' + job_data.get('description_text', '')
            )
            
            # Calculate weighted overall score
            overall_score = (
                (skills_result['overall'] * 0.6) +
                (experience_result['score'] * 0.3) +
                (education_result['score'] * 0.1)
            )
            
            # Determine recommendation
            recommendation = self.get_recommendation(overall_score, skills_result, experience_result)
            
            return {
                'overall_score': round(overall_score, 2),
                'skills': skills_result,
                'experience': experience_result,
                'education': education_result,
                'recommendation': recommendation,
                'match_breakdown': {
                    'skills_weight': 60,
                    'experience_weight': 30,
                    'education_weight': 10
                }
            }
            
        except Exception as e:
            logging.error(f"Error calculating enhanced match score: {e}")
            return {
                'overall_score': 0.0,
                'error': str(e)
            }
    
    def get_recommendation(self, overall_score: float, skills_result: Dict, experience_result: Dict) -> Dict[str, str]:
        """Generate hiring recommendation based on scores"""
        if overall_score >= 85:
            status = "Highly Recommended"
            reason = "Strong match across all criteria"
        elif overall_score >= 70:
            status = "Recommended"
            reason = "Good overall match with minor gaps"
        elif overall_score >= 55:
            status = "Consider"
            reason = "Moderate match, may need additional evaluation"
        elif overall_score >= 40:
            status = "Weak Match"
            reason = "Significant gaps in requirements"
        else:
            status = "Not Recommended"
            reason = "Poor match for this position"
        
        # Add specific insights
        insights = []
        if skills_result['required'] < 70:
            insights.append("Missing critical required skills")
        if experience_result['score'] < 60:
            insights.append("Experience level mismatch")
        if skills_result['required'] > 90 and experience_result['score'] > 85:
            insights.append("Excellent technical fit")
        
        return {
            'status': status,
            'reason': reason,
            'insights': insights
        }

# Create global instance
enhanced_job_matcher = EnhancedJobMatcher()