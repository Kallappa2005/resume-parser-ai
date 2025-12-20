from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.database import db, init_db
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from routes.resume_routes import resume_bp
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions
    CORS(app)
    JWTManager(app)
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(job_bp, url_prefix='/api/jobs')
    app.register_blueprint(resume_bp, url_prefix='/api/resumes')
    
    # Create database tables
    with app.app_context():
        init_db()
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'OK', 'message': 'Resume Parser API is running'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)