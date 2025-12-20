from config.database import db
from datetime import datetime
import json

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    resume_text = db.Column(db.Text, nullable=True)
    parsed_data = db.Column(db.Text, nullable=True)  # JSON string of parsed resume data
    match_score = db.Column(db.Float, nullable=True, default=0.0)
    status = db.Column(db.Enum('pending', 'shortlisted', 'rejected', 'deleted', name='resume_status'), 
                      default='pending')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_parsed_data(self, parsed_dict):
        """Convert parsed data dictionary to JSON string"""
        if parsed_dict:
            self.parsed_data = json.dumps(parsed_dict)
    
    def get_parsed_data(self):
        """Convert JSON string back to parsed data dictionary"""
        if self.parsed_data:
            try:
                return json.loads(self.parsed_data)
            except:
                return {}
        return {}
    
    def to_dict(self, include_job_details=False):
        """Convert resume to dictionary"""
        result = {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'filename': self.filename,
            'parsed_data': self.get_parsed_data(),
            'match_score': self.match_score,
            'status': self.status,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_job_details and self.job:
            result['job_title'] = self.job.title
            result['company'] = self.job.company
        
        if self.candidate:
            result['candidate_name'] = self.candidate.name
            result['candidate_email'] = self.candidate.email
        
        return result
    
    def __repr__(self):
        return f'<Resume {self.filename}>'