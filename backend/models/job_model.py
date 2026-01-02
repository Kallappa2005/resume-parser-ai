from config.database import db
from datetime import datetime
import json

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    description_text = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    skills_required = db.Column(db.Text, nullable=True)  # JSON string of required skills
    skills_preferred = db.Column(db.Text, nullable=True)  # JSON string of preferred skills
    benefits = db.Column(db.Text, nullable=True)
    job_type = db.Column(db.String(50), nullable=True, default='Full-time')
    extracted_skills = db.Column(db.Text, nullable=True)  # JSON string of skills list
    experience_required = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    salary_range = db.Column(db.String(100), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)  # Track job post views
    archived_at = db.Column(db.DateTime, nullable=True)  # Track when job was archived
    
    # Relationships
    resumes = db.relationship('Resume', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def set_skills(self, skills_list):
        """Convert skills list to JSON string"""
        if skills_list:
            self.extracted_skills = json.dumps(skills_list)
            
    def set_skills_required(self, skills_list):
        """Convert required skills list to JSON string"""
        if skills_list:
            self.skills_required = json.dumps(skills_list)
            
    def set_skills_preferred(self, skills_list):
        """Convert preferred skills list to JSON string"""
        if skills_list:
            self.skills_preferred = json.dumps(skills_list)
    
    def get_skills(self):
        """Convert JSON string back to skills list"""
        if self.extracted_skills:
            try:
                return json.loads(self.extracted_skills)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
        
    def get_skills_required(self):
        """Convert required skills JSON string back to skills list"""
        if self.skills_required:
            try:
                return json.loads(self.skills_required)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
        
    def get_skills_preferred(self):
        """Convert preferred skills JSON string back to skills list"""
        if self.skills_preferred:
            try:
                return json.loads(self.skills_preferred)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def to_dict(self, include_resumes=False):
        """Convert job description to dictionary"""
        result = {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'description_text': self.description_text,
            'requirements': self.requirements,
            'skills_required': self.get_skills_required(),
            'skills_preferred': self.get_skills_preferred(),
            'benefits': self.benefits,
            'job_type': self.job_type,
            'extracted_skills': self.get_skills(),
            'experience_required': self.experience_required,
            'location': self.location,
            'salary_range': self.salary_range,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'view_count': self.view_count,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None
        }
        
        if include_resumes:
            active_resumes = [resume for resume in self.resumes if resume.status != 'deleted']
            result['resumes_count'] = len(active_resumes)
            result['resumes'] = [resume.to_dict() for resume in active_resumes]
            
            # Add analytics data
            result['applications_by_status'] = {
                'pending': len([r for r in active_resumes if r.status == 'pending']),
                'shortlisted': len([r for r in active_resumes if r.status == 'shortlisted']),
                'rejected': len([r for r in active_resumes if r.status == 'rejected']),
                'hired': len([r for r in active_resumes if r.status == 'hired'])
            }
            
            # Calculate average match score
            match_scores = [r.match_score for r in active_resumes if r.match_score]
            result['avg_match_score'] = sum(match_scores) / len(match_scores) if match_scores else 0
        
        return result
    
    def __repr__(self):
        return f'<JobDescription {self.title}>'