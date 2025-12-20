from config.database import db
from datetime import datetime
import json

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    description_text = db.Column(db.Text, nullable=False)
    extracted_skills = db.Column(db.Text, nullable=True)  # JSON string of skills list
    experience_required = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    salary_range = db.Column(db.String(100), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    resumes = db.relationship('Resume', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def set_skills(self, skills_list):
        """Convert skills list to JSON string"""
        if skills_list:
            self.extracted_skills = json.dumps(skills_list)
    
    def get_skills(self):
        """Convert JSON string back to skills list"""
        if self.extracted_skills:
            try:
                return json.loads(self.extracted_skills)
            except:
                return []
        return []
    
    def to_dict(self, include_resumes=False):
        """Convert job description to dictionary"""
        result = {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'description_text': self.description_text,
            'extracted_skills': self.get_skills(),
            'experience_required': self.experience_required,
            'location': self.location,
            'salary_range': self.salary_range,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
        
        if include_resumes:
            result['resumes_count'] = len(self.resumes)
            result['resumes'] = [resume.to_dict() for resume in self.resumes if resume.status != 'deleted']
        
        return result
    
    def __repr__(self):
        return f'<JobDescription {self.title}>'