from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_model import User
from models.job_model import JobDescription
from models.resume_model import Resume
from config.database import db

job_bp = Blueprint('jobs', __name__)

@job_bp.route('/create', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job description (HR only)"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Check if user is HR
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can create job descriptions'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description_text']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Title and description are required'}), 400
        
        # Create new job description
        job = JobDescription(
            title=data['title'],
            company=data.get('company', ''),
            description_text=data['description_text'],
            experience_required=data.get('experience_required', ''),
            location=data.get('location', ''),
            salary_range=data.get('salary_range', ''),
            created_by=user_id
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'message': 'Job description created successfully',
            'job': job.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create job: {str(e)}'}), 500

@job_bp.route('/list', methods=['GET'])
@jwt_required()
def list_jobs():
    """List all active job descriptions"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # HR sees jobs they created, Candidates see all active jobs
        if user.role == 'HR':
            jobs = JobDescription.query.filter_by(
                created_by=user_id, 
                is_active=True
            ).order_by(JobDescription.created_at.desc()).all()
        else:
            jobs = JobDescription.query.filter_by(
                is_active=True
            ).order_by(JobDescription.created_at.desc()).all()
        
        jobs_list = [job.to_dict() for job in jobs]
        
        return jsonify({
            'jobs': jobs_list,
            'total': len(jobs_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list jobs: {str(e)}'}), 500

@job_bp.route('/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_details(job_id):
    """Get job description details with resumes (HR only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # HR can see their own jobs with resumes, Candidates see basic job info
        if user.role == 'HR':
            if job.created_by != user_id:
                return jsonify({'error': 'Access denied'}), 403
            return jsonify({'job': job.to_dict(include_resumes=True)}), 200
        else:
            return jsonify({'job': job.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get job details: {str(e)}'}), 500

@job_bp.route('/<int:job_id>/resumes', methods=['GET'])
@jwt_required()
def get_job_resumes():
    """Get all resumes for a specific job (HR only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is HR
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can view resumes'}), 403
        
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if HR owns this job
        if job.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get resumes sorted by match score (highest first)
        resumes = Resume.query.filter_by(
            job_id=job_id
        ).filter(
            Resume.status != 'deleted'
        ).order_by(
            Resume.match_score.desc()
        ).all()
        
        resumes_list = [resume.to_dict(include_job_details=True) for resume in resumes]
        
        return jsonify({
            'job': job.to_dict(),
            'resumes': resumes_list,
            'total': len(resumes_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get job resumes: {str(e)}'}), 500

@job_bp.route('/<int:job_id>/update', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update job description (HR only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is HR
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can update job descriptions'}), 403
        
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if HR owns this job
        if job.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            job.title = data['title']
        if 'company' in data:
            job.company = data['company']
        if 'description_text' in data:
            job.description_text = data['description_text']
        if 'experience_required' in data:
            job.experience_required = data['experience_required']
        if 'location' in data:
            job.location = data['location']
        if 'salary_range' in data:
            job.salary_range = data['salary_range']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update job: {str(e)}'}), 500