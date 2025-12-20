from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_model import User
from models.job_model import JobDescription
from models.resume_model import Resume
from config.database import db
import os
from datetime import datetime
from werkzeug.utils import secure_filename

resume_bp = Blueprint('resumes', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resume_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    """Upload resume for a specific job (Candidate only)"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Check if user is Candidate
        if not user or user.role != 'Candidate':
            return jsonify({'error': 'Only candidates can upload resumes'}), 403
        
        # Check if file is present
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        job_id = request.form.get('job_id')
        
        # Validate inputs
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not job_id:
            return jsonify({'error': 'Job ID is required'}), 400
        
        # Check if job exists
        job = JobDescription.query.get(job_id)
        if not job or not job.is_active:
            return jsonify({'error': 'Job not found or inactive'}), 404
        
        # Check if candidate already applied to this job
        existing_resume = Resume.query.filter_by(
            candidate_id=user_id, 
            job_id=job_id
        ).filter(Resume.status != 'deleted').first()
        
        if existing_resume:
            return jsonify({'error': 'You have already applied to this job'}), 409
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF, DOC, and DOCX files are allowed'}), 400
        
        # Create upload directory if it doesn't exist
        upload_folder = os.path.join(os.getcwd(), 'uploads', 'resumes')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        timestamp = int(datetime.now().timestamp())
        filename = f"{user_id}_{job_id}_{timestamp}_{filename}"
        file_path = os.path.join(upload_folder, filename)
        
        # Save file
        file.save(file_path)
        
        # Create resume record
        resume = Resume(
            candidate_id=user_id,
            job_id=job_id,
            filename=filename,
            file_path=file_path,
            status='pending'
        )
        
        db.session.add(resume)
        db.session.commit()
        
        return jsonify({
            'message': 'Resume uploaded successfully',
            'resume': resume.to_dict(include_job_details=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to upload resume: {str(e)}'}), 500

@resume_bp.route('/my-applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    """Get all applications by current candidate"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Check if user is Candidate
        if not user or user.role != 'Candidate':
            return jsonify({'error': 'Only candidates can view their applications'}), 403
        
        # Get all resumes by this candidate
        resumes = Resume.query.filter_by(
            candidate_id=user_id
        ).filter(
            Resume.status != 'deleted'
        ).order_by(
            Resume.uploaded_at.desc()
        ).all()
        
        applications = [resume.to_dict(include_job_details=True) for resume in resumes]
        
        return jsonify({
            'applications': applications,
            'total': len(applications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get applications: {str(e)}'}), 500

@resume_bp.route('/<int:resume_id>/status', methods=['PUT'])
@jwt_required()
def update_resume_status(resume_id):
    """Update resume status (HR only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is HR
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can update resume status'}), 403
        
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Check if HR owns the job this resume was applied to
        if resume.job.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'shortlisted', 'rejected']:
            return jsonify({'error': 'Invalid status'}), 400
        
        resume.status = new_status
        db.session.commit()
        
        return jsonify({
            'message': f'Resume status updated to {new_status}',
            'resume': resume.to_dict(include_job_details=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update resume status: {str(e)}'}), 500

@resume_bp.route('/<int:resume_id>/details', methods=['GET'])
@jwt_required()
def get_resume_details(resume_id):
    """Get detailed resume information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Check access permissions
        if user.role == 'Candidate':
            # Candidates can only see their own resumes
            if resume.candidate_id != user_id:
                return jsonify({'error': 'Access denied'}), 403
        elif user.role == 'HR':
            # HR can only see resumes for jobs they created
            if resume.job.created_by != user_id:
                return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'resume': resume.to_dict(include_job_details=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get resume details: {str(e)}'}), 500