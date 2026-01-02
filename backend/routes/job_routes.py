from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_model import User
from models.job_model import JobDescription
from models.resume_model import Resume
from config.database import db
from datetime import datetime

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
            requirements=data.get('requirements', ''),
            benefits=data.get('benefits', ''),
            job_type=data.get('job_type', 'Full-time'),
            experience_required=data.get('experience_required', ''),
            location=data.get('location', ''),
            salary_range=data.get('salary_range', ''),
            is_active=data.get('is_active', True),
            created_by=user_id
        )
        
        # Handle skills_required field
        skills_required = data.get('skills_required', [])
        if isinstance(skills_required, list):
            job.set_skills_required(skills_required)
        
        # Handle skills_preferred field
        skills_preferred = data.get('skills_preferred', [])
        if isinstance(skills_preferred, list):
            job.set_skills_preferred(skills_preferred)
        
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
    """List job descriptions with filtering options"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        include_archived = request.args.get('include_archived', 'false').lower() == 'true'
        
        # HR sees jobs they created, Candidates see all active jobs
        if user.role == 'HR':
            query = JobDescription.query.filter_by(created_by=user_id)
            if not include_archived:
                query = query.filter_by(is_active=True)
            jobs = query.order_by(JobDescription.created_at.desc()).all()
        else:
            jobs = JobDescription.query.filter_by(
                is_active=True
            ).order_by(JobDescription.created_at.desc()).all()
        
        jobs_list = [job.to_dict(include_resumes=True) for job in jobs]
        
        return jsonify({
            'jobs': jobs_list,
            'total': len(jobs_list),
            'active_count': len([j for j in jobs if j.is_active]),
            'archived_count': len([j for j in jobs if not j.is_active])
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list jobs: {str(e)}'}), 500

@job_bp.route('/<int:job_id>/archive', methods=['PUT'])
@jwt_required()
def archive_job(job_id):
    """Archive/deactivate job (HR only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can archive jobs'}), 403
        
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
            
        if job.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Toggle archived status
        job.is_active = not job.is_active
        if not job.is_active:
            job.archived_at = datetime.utcnow()
        else:
            job.archived_at = None
            
        job.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'archived' if not job.is_active else 'reactivated'
        return jsonify({
            'message': f'Job {status} successfully',
            'job': job.to_dict(include_resumes=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to archive job: {str(e)}'}), 500

@job_bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update job description (HR only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can update job descriptions'}), 403
        
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
            
        if job.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update job fields
        if 'title' in data:
            job.title = data['title']
        if 'company' in data:
            job.company = data['company']
        if 'description_text' in data:
            job.description_text = data['description_text']
        if 'requirements' in data:
            job.requirements = data['requirements']
        if 'benefits' in data:
            job.benefits = data['benefits']
        if 'job_type' in data:
            job.job_type = data['job_type']
        if 'experience_required' in data:
            job.experience_required = data['experience_required']
        if 'location' in data:
            job.location = data['location']
        if 'salary_range' in data:
            job.salary_range = data['salary_range']
        if 'is_active' in data:
            job.is_active = data['is_active']
            
        # Handle skills updates
        if 'skills_required' in data and isinstance(data['skills_required'], list):
            job.set_skills_required(data['skills_required'])
        if 'skills_preferred' in data and isinstance(data['skills_preferred'], list):
            job.set_skills_preferred(data['skills_preferred'])
        
        # Update timestamp
        job.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Job updated successfully',
            'job': job.to_dict(include_resumes=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update job: {str(e)}'}), 500
    """Get job description details with resumes (HR only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Track view for analytics (only for candidate views)
        if user.role == 'Candidate':
            job.view_count += 1
            db.session.commit()
            
        # HR can see their own jobs with resumes, Candidates see basic job info
        if user.role == 'HR':
            if job.created_by != user_id:
                return jsonify({'error': 'Access denied'}), 403
            return jsonify({'job': job.to_dict(include_resumes=True)}), 200
        else:
            return jsonify({'job': job.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get job details: {str(e)}'}), 500

@job_bp.route('/<int:job_id>/analytics', methods=['GET'])
@jwt_required()
def get_job_analytics(job_id):
    """Get comprehensive job analytics (HR only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can view analytics'}), 403
        
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
            
        if job.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all resumes for this job
        resumes = Resume.query.filter_by(job_id=job_id).filter(Resume.status != 'deleted').all()
        
        # Calculate analytics
        analytics = {
            'job_info': job.to_dict(),
            'total_views': job.view_count,
            'total_applications': len(resumes),
            'applications_by_status': {
                'pending': len([r for r in resumes if r.status == 'pending']),
                'shortlisted': len([r for r in resumes if r.status == 'shortlisted']), 
                'rejected': len([r for r in resumes if r.status == 'rejected']),
                'hired': len([r for r in resumes if r.status == 'hired'])
            },
            'match_score_stats': {},
            'application_timeline': [],
            'top_skills_found': {},
            'experience_distribution': {}
        }
        
        if resumes:
            # Match score statistics
            match_scores = [r.match_score for r in resumes if r.match_score]
            if match_scores:
                analytics['match_score_stats'] = {
                    'average': round(sum(match_scores) / len(match_scores), 1),
                    'highest': max(match_scores),
                    'lowest': min(match_scores),
                    'above_70': len([s for s in match_scores if s >= 70]),
                    'above_80': len([s for s in match_scores if s >= 80])
                }
            
            # Application timeline (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_applications = [r for r in resumes if r.uploaded_at >= thirty_days_ago]
            
            # Group by date
            timeline = {}
            for resume in recent_applications:
                date_key = resume.uploaded_at.strftime('%Y-%m-%d')
                timeline[date_key] = timeline.get(date_key, 0) + 1
            
            analytics['application_timeline'] = [{'date': k, 'count': v} for k, v in sorted(timeline.items())]
            
            # Top skills found in applications
            skills_count = {}
            experience_years = []
            
            for resume in resumes:
                parsed_data = resume.get_parsed_data()
                if parsed_data:
                    # Count skills
                    skills = parsed_data.get('skills', [])
                    for skill in skills:
                        skills_count[skill] = skills_count.get(skill, 0) + 1
                    
                    # Collect experience years
                    exp_years = parsed_data.get('total_experience_years', 0)
                    if exp_years:
                        experience_years.append(exp_years)
            
            # Top 10 skills
            top_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]
            analytics['top_skills_found'] = [{'skill': k, 'count': v} for k, v in top_skills]
            
            # Experience distribution
            if experience_years:
                analytics['experience_distribution'] = {
                    'average': round(sum(experience_years) / len(experience_years), 1),
                    '0-2_years': len([e for e in experience_years if 0 <= e <= 2]),
                    '3-5_years': len([e for e in experience_years if 3 <= e <= 5]),
                    '6-10_years': len([e for e in experience_years if 6 <= e <= 10]),
                    '10+_years': len([e for e in experience_years if e > 10])
                }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get analytics: {str(e)}'}), 500

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