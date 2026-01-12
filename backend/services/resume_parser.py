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
        """Extract text from PDF file using multiple methods"""
        text = ""
        
        try:
            # Method 1: Try PyPDF2 first
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # If we got substantial text, return it
            if len(text.strip()) > 50:
                return text.strip()
            
            # Method 2: Try alternative approach with more flexible extraction
            logging.warning(f"PyPDF2 extracted minimal text ({len(text)} chars), trying alternative method")
            
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                alternative_text = ""
                for page in doc:
                    alternative_text += page.get_text() + "\n"
                doc.close()
                
                if len(alternative_text.strip()) > len(text.strip()):
                    logging.info("PyMuPDF extracted more text, using it")
                    return alternative_text.strip()
                    
            except ImportError:
                logging.warning("PyMuPDF not available, install with: pip install PyMuPDF")
            except Exception as e:
                logging.warning(f"PyMuPDF extraction failed: {e}")
            
            # Return whatever we got
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
        
        # Look for experience sections and also scan full text for experience mentions
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
        
        # Enhanced job parsing patterns for the specific format in the resume
        exp_patterns = [
            # Pattern 1: "Position | Company | Date - Date (Duration)" - Main format
            r'([A-Z][a-zA-Z\s]+(?:Developer|Engineer|Manager|Analyst|Specialist|Programmer)[^|\n]*?)\s*\|\s*([^|\n]+?(?:LLC|Inc|Corp|Company|Solutions|Group|Tech)[^|\n]*?)\s*\|\s*([A-Za-z]+ \d{4} - (?:Present|[A-Za-z]+ \d{4}))',
            
            # Pattern 2: Job title on separate line, company and dates following
            r'([A-Z][a-zA-Z\s]+(?:Developer|Engineer|Manager|Analyst|Specialist))\s*[\n\r]+([^|\n]+(?:LLC|Inc|Corp|Company|Solutions|Group))[^|\n]*[\n\r]*([A-Za-z]+ \d{4} - (?:Present|[A-Za-z]+ \d{4}))',
            
            # Pattern 3: Simple "Position | Company" format (company names with common suffixes)
            r'([A-Z][a-zA-Z\s]+(?:Developer|Engineer|Manager|Analyst|Specialist)[^|\n]*?)\s*\|\s*([A-Z][^|\n]+?(?:LLC|Inc|Corp|Company|Solutions|Group|Tech))',
            
            # Pattern 4: Alternative format with "at" 
            r'([A-Z][a-zA-Z\s]+(?:Developer|Engineer|Manager)[^|\n]*?)\s+at\s+([A-Z][^|\n]+?)\s*(?:\||\n)',
        ]
        
        # First, look for date ranges in the experience section
        date_ranges = []
        date_patterns = [
            r'([A-Za-z]+ \d{4})\s*-\s*(Present|[A-Za-z]+ \d{4})\s*(?:\([^)]+\))?',  # "Jan 2021 - Present (3 years)"
            r'(\d{4})\s*-\s*(Present|\d{4})',                                        # "2021 - Present"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, experience_section, re.IGNORECASE)
            for start_date, end_date in matches:
                date_ranges.append((start_date.strip(), end_date.strip()))
        
        # Parse job entries with improved logic
        for pattern in exp_patterns:
            matches = re.findall(pattern, experience_section, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                position = match[0].strip()
                company = match[1].strip()
                duration = match[2].strip() if len(match) > 2 and match[2].strip() else ""
                
                # Clean up position and company
                if not position or not company:
                    continue
                    
                # If no duration captured in the pattern, try to find matching date range
                if not duration and date_ranges:
                    for i, (start_date, end_date) in enumerate(date_ranges):
                        duration = f"{start_date} - {end_date}"
                        date_ranges.pop(i)  # Remove used date range
                        break
                
                exp_dict = {
                    'position': position,
                    'company': company,  
                    'duration': duration or 'Not specified'
                }
                experiences.append(exp_dict)
        
        # If structured parsing failed but we have date ranges, create generic entries
        if not experiences and date_ranges:
            for i, (start_date, end_date) in enumerate(date_ranges):
                experiences.append({
                    'position': f'Position {i+1}',
                    'company': 'Company not specified',
                    'duration': f"{start_date} - {end_date}"
                })
        
        # Manual parsing for the specific Alex Smith format if patterns fail
        if not experiences:
            lines = experience_section.split('\n')
            current_job = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line contains job title + company + dates
                if '|' in line and ('Developer' in line or 'Engineer' in line or 'Manager' in line):
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) >= 2:
                        position = parts[0]
                        company_and_date = parts[1]
                        
                        # Try to separate company from date
                        company = company_and_date
                        duration = ""
                        
                        # Look for date pattern at end
                        date_match = re.search(r'([A-Za-z]+ \d{4} - (?:Present|[A-Za-z]+ \d{4}))', company_and_date)
                        if date_match:
                            duration = date_match.group(1)
                            company = company_and_date.replace(duration, '').strip()
                        
                        experiences.append({
                            'position': position,
                            'company': company,
                            'duration': duration or 'Not specified'
                        })
        
        # Calculate total experience more intelligently
        duration_text = (experience_section + " " + text).lower()
        
        # Priority 1: Look for explicit professional summary mentions (most reliable)
        summary_patterns = [
            r'(?:experienced|seasoned|senior).*?with\s*(\d+)\s*years?\s*of\s*(?:expertise|experience)',
            r'(\d+)\s*years?\s*of\s*(?:expertise|experience).*?(?:developer|engineer|professional)',
            r'professional.*?with\s*(\d+)\s*years?',
        ]
        
        summary_years = []
        for pattern in summary_patterns:
            matches = re.findall(pattern, duration_text)
            for match in matches:
                try:
                    years = int(match)
                    if 0 < years <= 50:  # Reasonable range
                        summary_years.append(years)
                except (ValueError, TypeError):
                    continue
        
        # Priority 2: Calculate from actual job date ranges
        calculated_years = []
        for start_date, end_date in date_ranges:
            try:
                start_year = int(re.search(r'\d{4}', start_date).group())
                current_year = 2026
                
                if 'present' in end_date.lower() or 'current' in end_date.lower():
                    end_year = current_year
                else:
                    end_year_match = re.search(r'\d{4}', end_date)
                    end_year = int(end_year_match.group()) if end_year_match else current_year
                
                if start_year > 0 and end_year >= start_year:
                    duration = end_year - start_year
                    calculated_years.append(max(duration, 1))  # At least 1 year for current jobs
                        
            except (ValueError, AttributeError):
                continue
        
        # Priority 3: Look for explicit duration mentions in job descriptions
        job_duration_patterns = [
            r'\((\d+)\s*years?\)',      # "(3 years)"
            r'\((\d+)\s*months?\)',     # "(6 months)" 
        ]
        
        explicit_years = []
        explicit_months = []
        for pattern in job_duration_patterns:
            matches = re.findall(pattern, duration_text)
            for match in matches:
                try:
                    value = int(match)
                    if 'year' in pattern:
                        explicit_years.append(value)
                    else:  # months
                        explicit_months.append(value)
                except (ValueError, TypeError):
                    continue
        
        # Determine final total years using priority system
        if summary_years:
            # Trust professional summary most (like "3 years of expertise")
            total_years = max(summary_years)
        elif explicit_years:
            # Use explicit job duration mentions
            total_years = sum(explicit_years) + sum(explicit_months) // 12
        elif calculated_years:
            # Use calculated years from date ranges
            total_years = sum(calculated_years)
        else:
            # Fallback to number of jobs or convert months
            total_years = len(experiences) + sum(explicit_months) // 12
        
        return experiences, max(total_years, 0)
    
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