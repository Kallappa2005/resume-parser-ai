from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_model import User
from models.job_model import JobDescription
from models.resume_model import Resume
from config.database import db
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from services.resume_parser import resume_parser, job_matcher
from services.enhanced_job_matcher import enhanced_job_matcher

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
        
        # Parse resume using our parsing service
        try:
            parsed_data = resume_parser.parse_resume(file_path)
            
            # Calculate match score with enhanced job matcher
            job_data = {
                'skills_required': job.get_skills_required() or [],
                'skills_preferred': job.get_skills_preferred() or [],
                'extracted_skills': job.get_skills() or [],
                'experience_required': job.experience_required or '',
                'requirements': job.requirements or '',
                'description_text': job.description_text or ''
            }
            
            # Use enhanced matcher for detailed scoring
            match_result = enhanced_job_matcher.calculate_overall_match_score(parsed_data, job_data)
            match_score = match_result.get('overall_score', 0.0)
            
            # Store detailed match information
            parsed_data['match_details'] = match_result
            
        except Exception as parsing_error:
            print(f"Parsing error: {parsing_error}")
            # If parsing fails, continue with empty data
            parsed_data = {
                'raw_text': '',
                'skills': [],
                'experience': [],
                'education': [],
                'total_experience_years': 0,
                'parsing_status': 'failed'
            }
            match_score = 0
        
        # Create resume record with parsed data
        resume = Resume(
            candidate_id=user_id,
            job_id=job_id,
            filename=filename,
            file_path=file_path,
            match_score=match_score,
            status='pending'
        )
        
        # Use the model method to properly serialize parsed_data
        resume.set_parsed_data(parsed_data)
        
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

@resume_bp.route('/list', methods=['GET'])
@jwt_required()
def list_resumes():
    """Get all resumes with advanced search and filtering (HR only)"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Check if user is HR
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR can view all resumes'}), 403

        # Get query parameters for filtering
        search_query = request.args.get('search', '').strip().lower()
        status_filter = request.args.get('status', 'all')
        min_match_score = request.args.get('min_match_score', type=float)
        max_match_score = request.args.get('max_match_score', type=float) 
        min_experience = request.args.get('min_experience', type=int)
        max_experience = request.args.get('max_experience', type=int)
        job_id_filter = request.args.get('job_id', type=int)
        quick_filter = request.args.get('quick_filter', '')  # top_candidates, recent_applications
        sort_by = request.args.get('sort_by', 'uploaded_at')  # uploaded_at, match_score, candidate_name
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc

        # Start with base query
        query = Resume.query.filter(Resume.status != 'deleted')
        
        # Apply job filter
        if job_id_filter:
            query = query.filter(Resume.job_id == job_id_filter)
        
        # Apply status filter
        if status_filter and status_filter != 'all':
            query = query.filter(Resume.status == status_filter)
        
        # Apply match score range filter
        if min_match_score is not None:
            query = query.filter(Resume.match_score >= min_match_score)
        if max_match_score is not None:
            query = query.filter(Resume.match_score <= max_match_score)
            
        # Get all matching resumes
        resumes = query.all()
        
        # Convert to dictionaries with full details
        resume_list = []
        for resume in resumes:
            resume_dict = resume.to_dict(include_job_details=True)
            parsed_data = resume_dict['parsed_data'] or {}
            
            # Add computed fields for easier filtering
            resume_dict['total_experience_years'] = parsed_data.get('total_experience_years', 0)
            resume_dict['skills'] = parsed_data.get('skills', [])
            resume_dict['education'] = parsed_data.get('education', [])
            resume_dict['candidate_name'] = resume_dict.get('candidate_name', '')
            
            resume_list.append(resume_dict)
        
        # Apply search query filter (after getting parsed data)
        if search_query:
            filtered_resumes = []
            for resume in resume_list:
                # Search in candidate name
                if search_query in resume['candidate_name'].lower():
                    filtered_resumes.append(resume)
                    continue
                
                # Search in skills
                skills = resume.get('skills', [])
                if any(search_query in skill.lower() for skill in skills):
                    filtered_resumes.append(resume)
                    continue
                    
                # Search in job title
                if search_query in (resume.get('job_title', '')).lower():
                    filtered_resumes.append(resume)
                    continue
                    
                # Search in education
                education = resume.get('education', [])
                for edu in education:
                    if isinstance(edu, dict):
                        edu_text = f"{edu.get('degree', '')} {edu.get('field', '')} {edu.get('institution', '')}".lower()
                        if search_query in edu_text:
                            filtered_resumes.append(resume)
                            break
                            
            resume_list = filtered_resumes
        
        # Apply experience range filter
        if min_experience is not None or max_experience is not None:
            filtered_resumes = []
            for resume in resume_list:
                exp_years = resume.get('total_experience_years', 0)
                if min_experience is not None and exp_years < min_experience:
                    continue
                if max_experience is not None and exp_years > max_experience:
                    continue
                filtered_resumes.append(resume)
            resume_list = filtered_resumes
        
        # Apply quick filters
        if quick_filter == 'top_candidates':
            # Top 20% by match score or minimum 70% match
            if resume_list:
                min_score = max(70.0, sorted([r['match_score'] for r in resume_list], reverse=True)[int(len(resume_list) * 0.2)] if len(resume_list) > 5 else 70.0)
                resume_list = [r for r in resume_list if r['match_score'] >= min_score]
        elif quick_filter == 'recent_applications':
            # Applications from last 7 days
            from datetime import datetime, timedelta
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            resume_list = [r for r in resume_list if datetime.fromisoformat(r['uploaded_at'].replace('Z', '+00:00')) > seven_days_ago]
        
        # Apply sorting
        reverse_order = sort_order == 'desc'
        if sort_by == 'match_score':
            resume_list.sort(key=lambda x: x['match_score'] or 0, reverse=reverse_order)
        elif sort_by == 'candidate_name':
            resume_list.sort(key=lambda x: x['candidate_name'].lower(), reverse=reverse_order)
        elif sort_by == 'uploaded_at':
            resume_list.sort(key=lambda x: x['uploaded_at'] or '', reverse=reverse_order)
        elif sort_by == 'experience':
            resume_list.sort(key=lambda x: x.get('total_experience_years', 0), reverse=reverse_order)
        
        return jsonify({
            'resumes': resume_list,
            'count': len(resume_list),
            'total_before_filters': len(resumes)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get resumes: {str(e)}'}), 500

@resume_bp.route('/<int:resume_id>/download', methods=['GET'])
@jwt_required()
def download_resume(resume_id):
    """Download resume file (HR only)"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Check if user is HR
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR can download resumes'}), 403
        
        # Get the resume
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Check if file exists
        if not os.path.exists(resume.file_path):
            return jsonify({'error': 'Resume file not found on server'}), 404
        
        return send_file(
            resume.file_path,
            as_attachment=True,
            download_name=resume.filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to download resume: {str(e)}'}), 500

@resume_bp.route('/<int:resume_id>/status', methods=['PUT'])
@jwt_required()
def update_resume_status(resume_id):
    """Update resume status (HR only)"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
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

@resume_bp.route('/recalculate-scores', methods=['POST'])
@jwt_required()
def recalculate_all_match_scores():
    """Recalculate match scores for all resumes using enhanced algorithm"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role != 'hr':
            return jsonify({'error': 'Unauthorized. HR access required.'}), 403
        
        # Get all resumes
        resumes = Resume.query.filter(Resume.status != 'deleted').all()
        updated_count = 0
        
        for resume in resumes:
            try:
                # Get job data
                job = resume.job
                if not job:
                    continue
                
                job_data = {
                    'skills_required': job.get_skills_required() or [],
                    'skills_preferred': job.get_skills_preferred() or [],
                    'extracted_skills': job.get_skills() or [],
                    'experience_required': job.experience_required or '',
                    'requirements': job.requirements or '',
                    'description_text': job.description_text or ''
                }
                
                # Get parsed resume data
                parsed_data = resume.get_parsed_data()
                if not parsed_data:
                    continue
                
                # Calculate new match score
                match_result = enhanced_job_matcher.calculate_overall_match_score(parsed_data, job_data)
                new_score = match_result.get('overall_score', 0.0)
                
                # Update resume with new score and match details
                resume.match_score = new_score
                parsed_data['match_details'] = match_result
                resume.set_parsed_data(parsed_data)
                
                updated_count += 1
                
            except Exception as e:
                print(f"Error updating resume {resume.id}: {e}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully recalculated match scores for {updated_count} resumes',
            'updated_count': updated_count,
            'total_resumes': len(resumes)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to recalculate scores: {str(e)}'}), 500

@resume_bp.route('/<int:resume_id>/shortlist', methods=['PUT'])
@jwt_required()
def toggle_shortlist(resume_id):
    """Toggle shortlist status of a resume (HR only)"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Check if user is HR
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can shortlist candidates'}), 403
        
        # Get resume
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Toggle shortlist status
        if resume.status == 'shortlisted':
            resume.status = 'pending'
            action = 'removed from shortlist'
        else:
            resume.status = 'shortlisted'
            action = 'shortlisted'
        
        resume.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': f'Candidate {action} successfully',
            'resume_id': resume_id,
            'status': resume.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update shortlist status: {str(e)}'}), 500

@resume_bp.route('/compare', methods=['POST'])
@jwt_required()
def compare_resumes():
    """Compare multiple resumes side by side (HR only)"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Check if user is HR
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can compare resumes'}), 403
        
        data = request.get_json()
        resume_ids = data.get('resume_ids', [])
        
        if not resume_ids or len(resume_ids) < 2:
            return jsonify({'error': 'At least 2 resume IDs required for comparison'}), 400
        
        if len(resume_ids) > 5:
            return jsonify({'error': 'Maximum 5 resumes can be compared at once'}), 400
        
        # Get resumes
        resumes = Resume.query.filter(Resume.id.in_(resume_ids)).all()
        
        if len(resumes) != len(resume_ids):
            return jsonify({'error': 'One or more resumes not found'}), 404
        
        # Prepare comparison data
        comparison_data = {
            'resumes': [],
            'comparison_metrics': {
                'match_scores': [],
                'experience_levels': [],
                'skill_matches': [],
                'education_levels': []
            }
        }
        
        for resume in resumes:
            parsed_data = resume.get_parsed_data() or {}
            match_details = parsed_data.get('match_details', {})
            
            # Extract education information properly
            education_list = parsed_data.get('education', [])
            education_level = 'Not specified'
            if education_list:
                # Get the highest education level
                if isinstance(education_list, list) and education_list:
                    # Handle both dict and string formats
                    if isinstance(education_list[0], dict):
                        education_level = f"{education_list[0].get('degree', '')} {education_list[0].get('field', '')}".strip()
                        if not education_level:
                            education_level = education_list[0].get('description', 'Not specified')
                    else:
                        education_level = str(education_list[0])
                else:
                    education_level = str(education_list)
            
            # Extract experience properly
            experience_years = parsed_data.get('total_experience_years', 0)
            experience_list = parsed_data.get('experience', [])
            
            # Extract contact info properly
            contact_info = parsed_data.get('contact_info', {})
            
            # Extract projects and certifications
            projects = parsed_data.get('projects', [])
            certifications = parsed_data.get('certifications', [])
            
            # Extract skills properly
            skills = parsed_data.get('skills', [])
            
            resume_data = {
                'id': resume.id,
                'candidate_name': resume.candidate.name if resume.candidate else parsed_data.get('candidate_name', 'Unknown'),
                'candidate_email': resume.candidate.email if resume.candidate else contact_info.get('email', 'Unknown'),
                'filename': resume.filename,
                'match_score': resume.match_score or 0,
                'status': resume.status,
                'uploaded_at': resume.uploaded_at.isoformat() if resume.uploaded_at else None,
                
                # Properly extracted information
                'experience_years': experience_years,
                'experience_details': experience_list,
                'education_level': education_level,
                'education_details': education_list,
                'skills': skills,
                'projects': projects,
                'certifications': certifications,
                'contact_info': contact_info,
                
                # Match breakdown
                'match_breakdown': {
                    'skills_score': match_details.get('skills_score', 0),
                    'experience_score': match_details.get('experience_score', 0),
                    'education_score': match_details.get('education_score', 0),
                    'matched_skills': match_details.get('matched_skills', []),
                    'missing_skills': match_details.get('missing_skills', []),
                    'skills_weight': 60,
                    'experience_weight': 30,
                    'education_weight': 10
                }
            }
            
            comparison_data['resumes'].append(resume_data)
            
            # Add to comparison metrics with properly extracted data
            comparison_data['comparison_metrics']['match_scores'].append({
                'resume_id': resume.id,
                'score': resume.match_score or 0
            })
            comparison_data['comparison_metrics']['experience_levels'].append({
                'resume_id': resume.id,
                'years': experience_years
            })
            comparison_data['comparison_metrics']['skill_matches'].append({
                'resume_id': resume.id,
                'matched_count': len(match_details.get('matched_skills', [])),
                'total_skills': len(skills)
            })
            comparison_data['comparison_metrics']['education_levels'].append({
                'resume_id': resume.id,
                'level': education_level
            })
        
        # Sort resumes by match score (highest first)
        comparison_data['resumes'].sort(key=lambda x: x['match_score'], reverse=True)
        
        return jsonify(comparison_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to compare resumes: {str(e)}'}), 500

@resume_bp.route('/job/<int:job_id>/ranked', methods=['GET'])
@jwt_required()
def get_ranked_candidates(job_id):
    """Get ranked list of candidates for a specific job (HR only)"""
    try:
        # Convert string identity back to int
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Check if user is HR
        if not user or user.role != 'HR':
            return jsonify({'error': 'Only HR users can view ranked candidates'}), 403
        
        # Check if job exists
        job = JobDescription.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        status_filter = request.args.get('status', 'all')
        min_score = request.args.get('min_score', 0, type=float)
        
        # Build query
        query = Resume.query.filter_by(job_id=job_id)
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        if min_score > 0:
            query = query.filter(Resume.match_score >= min_score)
        
        # Get resumes ordered by match score (highest first)
        resumes = query.order_by(Resume.match_score.desc()).limit(limit).all()
        
        # Prepare ranked data
        ranked_candidates = []
        for index, resume in enumerate(resumes, 1):
            parsed_data = resume.get_parsed_data() or {}
            match_details = parsed_data.get('match_details', {})
            
            # Extract education information properly
            education_list = parsed_data.get('education', [])
            education_level = 'Not specified'
            if education_list:
                if isinstance(education_list, list) and education_list:
                    if isinstance(education_list[0], dict):
                        education_level = f"{education_list[0].get('degree', '')} {education_list[0].get('field', '')}".strip()
                        if not education_level:
                            education_level = education_list[0].get('description', 'Not specified')
                    else:
                        education_level = str(education_list[0])
                else:
                    education_level = str(education_list)
            
            # Extract experience properly
            experience_years = parsed_data.get('total_experience_years', 0)
            skills = parsed_data.get('skills', [])
            
            candidate_data = {
                'rank': index,
                'id': resume.id,
                'candidate_name': resume.candidate.name if resume.candidate else parsed_data.get('candidate_name', 'Unknown'),
                'candidate_email': resume.candidate.email if resume.candidate else 'Unknown',
                'filename': resume.filename,
                'match_score': resume.match_score or 0,
                'status': resume.status,
                'uploaded_at': resume.uploaded_at.isoformat() if resume.uploaded_at else None,
                
                # Key highlights for ranking view using correct field names
                'experience_years': experience_years,
                'education_level': education_level,
                'top_skills': skills[:5] if skills else [],  # Top 5 skills
                'matched_skills_count': len(match_details.get('matched_skills', [])),
                'total_skills_count': len(skills),
                
                # Quick metrics
                'skills_match_percentage': (len(match_details.get('matched_skills', [])) / 
                                          max(len(skills), 1)) * 100,
                'has_projects': len(parsed_data.get('projects', [])) > 0,
                'has_certifications': len(parsed_data.get('certifications', [])) > 0
            }
            
            ranked_candidates.append(candidate_data)
        
        return jsonify({
            'job_id': job_id,
            'job_title': job.title,
            'total_candidates': len(ranked_candidates),
            'ranking_criteria': 'Match Score (Skills 60% + Experience 30% + Education 10%)',
            'candidates': ranked_candidates
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get ranked candidates: {str(e)}'}), 500