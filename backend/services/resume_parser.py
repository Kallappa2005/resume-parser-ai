import spacy
import re
import json
from pathlib import Path
import PyPDF2
from docx import Document
import logging
from typing import Dict, List, Optional, Tuple
import dateutil.parser as date_parser
from datetime import datetime

class ResumeParser:
    def __init__(self):
        """Initialize the resume parser with spaCy model"""
        self.nlp = None
        try:
            # Try to load the spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logging.info("spaCy model loaded successfully")
        except OSError as e:
            logging.warning(f"spaCy model not found: {e}")
            logging.info("Falling back to basic text processing (install 'en_core_web_sm' for better results)")
        except Exception as e:
            logging.error(f"Failed to load spaCy model: {e}")
            logging.info("Using basic text processing without NLP model")
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from DOCX: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from resume file based on extension"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def extract_name(self, text: str) -> str:
        """Extract candidate name from resume text"""
        lines = text.strip().split('\n')
        
        # Usually the name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line.split()) >= 2 and len(line.split()) <= 4:
                # Check if it looks like a name (not email, phone, etc.)
                if not re.search(r'[@\d\+\-\(\)]', line) and len(line) > 3:
                    # Additional checks to avoid false positives
                    words = line.split()
                    if all(word.isalpha() or word.replace('.', '').isalpha() for word in words):
                        return line.title()
        
        return ""
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Enhanced contact information extraction"""
        contact_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['email'] = emails[0] if emails else ""
        
        # Extract phone number (enhanced patterns)
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}'
        ]
        
        phone = ""
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                phone = phones[0]
                break
        contact_info['phone'] = phone
        
        # Extract LinkedIn
        linkedin_patterns = [
            r'linkedin\.com/in/[\w-]+',
            r'linkedin\.com/[\w-]+',
            r'www\.linkedin\.com/in/[\w-]+'
        ]
        
        linkedin = ""
        for pattern in linkedin_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                linkedin = matches[0]
                break
        contact_info['linkedin'] = linkedin
        
        # Extract location/address
        location_patterns = [
            r'Location[:\s]+([^\n]+)',
            r'Address[:\s]+([^\n]+)',
            r'\b([A-Z][a-z]+,\s*[A-Z][a-z]+)\b',  # City, State
            r'\b([A-Z][a-z]+,\s*[A-Z]{2})\b'      # City, ST
        ]
        
        location = ""
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                location = matches[0]
                break
        contact_info['location'] = location
        
        return contact_info
    
    def extract_skills(self, text: str) -> List[str]:
        """Enhanced skills extraction with comprehensive keyword matching"""
        skills = set()
        text_lower = text.lower()
        
        # Comprehensive list of technical skills
        tech_skills = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c sharp', 'php', 'ruby', 
            'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash',
            
            # Web Frontend
            'html', 'css', 'react', 'reactjs', 'angular', 'angularjs', 'vue.js', 'vuejs', 'jquery',
            'bootstrap', 'tailwind', 'material ui', 'sass', 'scss', 'less', 'webpack', 'babel',
            
            # Web Backend  
            'node.js', 'nodejs', 'express.js', 'express', 'django', 'flask', 'fastapi', 
            'spring', 'spring boot', 'laravel', 'rails', 'asp.net', '.net', 'dotnet',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'sqlite', 'oracle',
            'cassandra', 'elasticsearch', 'dynamodb', 'neo4j', 'sql server',
            
            # Cloud Platforms
            'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud',
            'heroku', 'digitalocean', 'linode',
            
            # DevOps & Tools
            'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'terraform', 'ansible',
            'chef', 'puppet', 'vagrant', 'git', 'svn', 'mercurial',
            
            # Data Science & AI
            'machine learning', 'ml', 'artificial intelligence', 'ai', 'data science',
            'deep learning', 'neural networks', 'tensorflow', 'pytorch', 'keras',
            'scikit-learn', 'sklearn', 'pandas', 'numpy', 'matplotlib', 'seaborn',
            'jupyter', 'r studio', 'tableau', 'power bi',
            
            # Mobile Development
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'cordova', 'phonegap',
            
            # Others
            'rest api', 'restful', 'graphql', 'soap', 'microservices', 'agile', 'scrum',
            'devops', 'ci/cd', 'linux', 'unix', 'windows', 'macos', 'blockchain', 'iot',
            'version control', 'unit testing', 'integration testing', 'tdd', 'bdd'
        ]
        
        # Find skills in text
        for skill in tech_skills:
            # Check for exact matches
            if skill in text_lower:
                skills.add(skill.title() if skill.islower() else skill)
            
            # Check for word boundaries for single words
            if ' ' not in skill and re.search(rf'\b{re.escape(skill)}\b', text_lower):
                skills.add(skill.title() if skill.islower() else skill)
        
        # Special handling for common abbreviations and variations
        skill_variations = {
            'js': 'JavaScript', 'ts': 'TypeScript', 'py': 'Python', 
            'db': 'Database', 'api': 'API', 'ui': 'UI', 'ux': 'UX',
            'ml': 'Machine Learning', 'ai': 'Artificial Intelligence',
            'css3': 'CSS', 'html5': 'HTML', 'es6': 'JavaScript'
        }
        
        for abbr, full_name in skill_variations.items():
            if re.search(rf'\b{re.escape(abbr)}\b', text_lower):
                skills.add(full_name)
        
        return sorted(list(skills))
    
    def extract_experience(self, text: str) -> Tuple[List[Dict], int]:
        """Enhanced experience extraction with detailed parsing"""
        experiences = []
        total_years = 0
        
        # Look for experience sections
        experience_section = ""
        lines = text.split('\n')
        
        in_experience_section = False
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Detect experience section start
            if any(keyword in line_lower for keyword in ['experience', 'work history', 'employment', 'career']):
                in_experience_section = True
                continue
            
            # Stop at next major section
            if in_experience_section and any(keyword in line_lower for keyword in ['education', 'skills', 'projects', 'certifications']):
                break
                
            if in_experience_section:
                experience_section += line + "\n"
        
        # Parse individual experiences
        exp_patterns = [
            r'([A-Z][^|\n]*?)\s*(?:\||at|@)\s*([A-Z][^|\n]*?)\s*(?:\||\()([^)]*(?:months?|years?).*?)(?:\)|\n)',
            r'([A-Z][^|\n]*?)\s+\(([^)]*(?:months?|years?).*?)\)',
            r'([A-Z][^|\n]*?)\s*-\s*([^|\n]*?)\s*\(([^)]*(?:months?|years?).*?)\)'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, experience_section, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match) >= 2:
                    exp_dict = {
                        'position': match[0].strip(),
                        'company': match[1].strip() if len(match) > 1 else 'Not specified',
                        'duration': match[2].strip() if len(match) > 2 else 'Not specified'
                    }
                    experiences.append(exp_dict)
        
        # Calculate total experience from duration strings
        duration_text = experience_section.lower()
        
        # Look for year mentions
        year_matches = re.findall(r'(\d+)[\s\-]*years?', duration_text)
        month_matches = re.findall(r'(\d+)[\s\-]*months?', duration_text)
        
        years_from_years = sum(int(y) for y in year_matches) if year_matches else 0
        years_from_months = sum(int(m) for m in month_matches) // 12 if month_matches else 0
        
        total_years = max(years_from_years + years_from_months, len(experiences))
        
        return experiences, total_years
    
    def extract_education(self, text: str) -> List[Dict]:
        """Enhanced education extraction"""
        educations = []
        
        # Look for education section
        education_section = ""
        lines = text.split('\n')
        
        in_education_section = False
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in ['education', 'academic', 'qualification']):
                in_education_section = True
                continue
            
            if in_education_section and any(keyword in line_lower for keyword in ['experience', 'skills', 'projects', 'certifications']):
                break
                
            if in_education_section:
                education_section += line + "\n"
        
        # Education patterns
        degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'certificate',
            'b.tech', 'b.sc', 'm.tech', 'm.sc', 'mba', 'bba', 'be', 'me',
            'bs', 'ms', 'ba', 'ma', 'bca', 'mca'
        ]
        
        # Find degree information
        lines = education_section.split('\n')
        current_education = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            line_lower = line.lower()
            
            # Check for degree
            for keyword in degree_keywords:
                if keyword in line_lower:
                    if current_education:
                        educations.append(current_education)
                    current_education = {
                        'degree': line,
                        'institution': 'Not specified',
                        'year': 'Not specified'
                    }
                    break
            
            # Look for years (graduation year)
            year_matches = re.findall(r'\b(19|20)\d{2}\b', line)
            if year_matches and current_education:
                years = [int(y) for y in year_matches]
                if len(years) == 2:
                    current_education['year'] = f"{min(years)} - {max(years)}"
                else:
                    current_education['year'] = str(max(years))
            
            # If line doesn't contain degree keywords but we have current education,
            # it might be institution name
            if current_education and not any(k in line_lower for k in degree_keywords):
                if current_education['institution'] == 'Not specified' and len(line.split()) <= 6:
                    current_education['institution'] = line
        
        if current_education:
            educations.append(current_education)
        
        return educations
    
    def extract_projects(self, text: str) -> List[Dict]:
        """Extract project information"""
        projects = []
        
        # Look for projects section
        project_section = ""
        lines = text.split('\n')
        
        in_project_section = False
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in ['projects', 'project work', 'key projects']):
                in_project_section = True
                continue
            
            if in_project_section and any(keyword in line_lower for keyword in ['experience', 'skills', 'education', 'certifications']):
                break
                
            if in_project_section:
                project_section += line + "\n"
        
        # Parse projects
        project_lines = [line.strip() for line in project_section.split('\n') if line.strip()]
        current_project = None
        
        for line in project_lines:
            # Project titles are usually standalone lines or start with bullet points
            if (not line.startswith('•') and not line.startswith('-') and 
                not line.startswith('Built') and not line.startswith('Developed') and
                not line.startswith('Implemented') and len(line.split()) <= 8):
                
                if current_project:
                    projects.append(current_project)
                
                current_project = {
                    'name': line,
                    'description': '',
                    'technologies': []
                }
            
            elif current_project:
                # Add to description
                if current_project['description']:
                    current_project['description'] += " "
                current_project['description'] += line.lstrip('•-').strip()
        
        if current_project:
            projects.append(current_project)
        
        return projects
    
    def parse_resume(self, file_path: str) -> Dict:
        """Main method to parse resume and extract all information"""
        try:
            # Extract text from file
            text = self.extract_text(file_path)
            
            if not text:
                raise ValueError("Could not extract text from resume")
            
            # Extract candidate name
            candidate_name = self.extract_name(text)
            
            # Extract experience and calculate years
            experiences, total_experience_years = self.extract_experience(text)
            
            # Extract all information using enhanced methods
            parsed_data = {
                'raw_text': text,
                'candidate_name': candidate_name,
                'contact_info': self.extract_contact_info(text),
                'skills': self.extract_skills(text),
                'experience': experiences,
                'education': self.extract_education(text),
                'projects': self.extract_projects(text),
                'total_experience_years': total_experience_years,
                'parsing_status': 'success'
            }
            
            return parsed_data
            
        except Exception as e:
            logging.error(f"Error parsing resume: {e}")
            return {
                'raw_text': '',
                'candidate_name': '',
                'contact_info': {},
                'skills': [],
                'experience': [],
                'education': [],
                'projects': [],
                'total_experience_years': 0,
                'parsing_status': 'failed',
                'error': str(e)
            }

# Job matching functionality
class JobMatcher:
    def __init__(self):
        self.nlp = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            pass
    
    def calculate_skills_match(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skills match percentage"""
        if not job_skills:
            return 0.0
        
        # Convert to lowercase for comparison
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Find matching skills
        matching_skills = set(resume_skills_lower) & set(job_skills_lower)
        
        # Calculate percentage
        match_percentage = (len(matching_skills) / len(job_skills_lower)) * 100
        return round(match_percentage, 2)
    
    def calculate_experience_match(self, resume_years: float, required_experience: str) -> float:
        """Calculate experience match score"""
        # Extract years from requirement string
        experience_pattern = r'(\d+)[-\s]*(\d*)\s*(?:to\s*)?(?:\d*\s*)?years?'
        matches = re.findall(experience_pattern, required_experience.lower())
        
        if not matches:
            return 50.0  # Default score if can't parse requirement
        
        min_years = int(matches[0][0])
        max_years = int(matches[0][1]) if matches[0][1] else min_years + 2
        
        if resume_years >= min_years and resume_years <= max_years + 2:
            return 100.0
        elif resume_years >= min_years - 1:
            return 80.0
        elif resume_years >= min_years - 2:
            return 60.0
        else:
            return 30.0
    
    def calculate_match_score(self, parsed_resume: Dict, job_data: Dict) -> float:
        """Calculate overall match score between resume and job"""
        try:
            # Skills matching (60% weight)
            skills_match = self.calculate_skills_match(
                parsed_resume.get('skills', []),
                job_data.get('skills_required', [])
            )
            
            # Experience matching (30% weight)
            experience_match = self.calculate_experience_match(
                parsed_resume.get('total_experience_years', 0),
                job_data.get('experience_required', '')
            )
            
            # Education matching (10% weight) - simplified for now
            education_match = 70.0  # Default score
            
            # Calculate weighted score
            overall_score = (
                (skills_match * 0.6) + 
                (experience_match * 0.3) + 
                (education_match * 0.1)
            )
            
            return round(overall_score, 2)
            
        except Exception as e:
            logging.error(f"Error calculating match score: {e}")
            return 0.0

# Global instances
resume_parser = ResumeParser()
job_matcher = JobMatcher()