# 🚀 Resume Parser AI - Smart Hiring Platform

A full-stack AI/ML-powered Resume Parser and Job Description Matching Web Application designed to streamline the hiring process with intelligent resume analysis and candidate-job matching.

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Usage](#-usage)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🏢 HR Dashboard
- **Job Management**: Create, edit, and manage job postings
- **Application Review**: View and manage candidate applications
- **Resume Analysis**: AI-powered resume parsing and skills extraction
- **Candidate Matching**: Smart matching algorithms for job-candidate fit
- **Analytics Dashboard**: Hiring metrics and insights
- **Status Management**: Track application status (pending, shortlisted, rejected, hired)

### 👤 Candidate Dashboard
- **Job Discovery**: Browse available job opportunities
- **Smart Application**: AI-powered resume-job matching scores
- **Application Tracking**: Monitor application status and progress
- **Profile Management**: Manage personal information and skills
- **Resume Upload**: Support for PDF and DOCX formats

### 🤖 AI/ML Features
- **Resume Parsing**: Extract structured data from resume documents
- **Skills Recognition**: Identify and categorize technical and soft skills
- **Job Matching**: Calculate compatibility scores between resumes and job descriptions
- **NLP Processing**: Advanced text analysis using spaCy
- **Machine Learning**: Continuous improvement of matching algorithms

## 🛠 Technology Stack

### Frontend
- **React.js 18** - Modern JavaScript library for building user interfaces
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework for styling
- **React Router** - Client-side routing
- **Axios/Fetch API** - HTTP client for API communication

### Backend
- **Python 3.11+** - Core backend language
- **Flask 3.0** - Lightweight web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database for development
- **JWT** - JSON Web Tokens for authentication
- **spaCy** - Natural language processing library
- **scikit-learn** - Machine learning algorithms
- **PyPDF2** - PDF document processing
- **python-docx** - Word document processing

### Development Tools
- **Git** - Version control
- **VS Code** - Recommended IDE
- **Postman** - API testing
- **npm/pip** - Package managers

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**
- **Node.js 16 or higher**
- **npm or yarn**
- **Git**

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Kallappa2005/resume-parser-ai.git
cd resume-parser-ai
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Create environment file
copy .env.example .env
# Edit .env file with your configuration
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Create environment file (if needed)
cp .env.example .env.local
# Edit .env.local with your configuration
```

### 4. Database Setup

```bash
# Navigate back to backend directory
cd ../backend

# Initialize database
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

## 🏃‍♂️ Running the Application

### Development Mode

#### Start Backend Server

```bash
cd backend

# Activate virtual environment (if not already activated)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Run Flask development server
python app.py
```

The backend will be available at: `http://localhost:5000`

#### Start Frontend Server

```bash
cd frontend

# Run Vite development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### Production Mode

#### Backend (Flask)

```bash
cd backend

# Set production environment
export FLASK_ENV=production  # Linux/macOS
set FLASK_ENV=production     # Windows

# Run with Gunicorn (recommended for production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Frontend (React)

```bash
cd frontend

# Build for production
npm run build

# Serve built files (using serve package)
npm install -g serve
serve -s dist -l 3000
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/verify-token` - Verify JWT token

### Jobs (HR Only)
- `GET /api/jobs/list` - Get all jobs
- `POST /api/jobs/create` - Create new job
- `GET /api/jobs/{id}` - Get job details
- `PUT /api/jobs/{id}` - Update job
- `DELETE /api/jobs/{id}` - Delete job

### Resumes
- `POST /api/resumes/upload` - Upload resume
- `GET /api/resumes/my-applications` - Get user applications
- `GET /api/resumes/job/{job_id}` - Get job applications (HR only)
- `PUT /api/resumes/{id}/status` - Update application status
- `GET /api/resumes/{id}` - Get resume details

## 📁 Project Structure

```
resume-parser-ai/
├── backend/                    # Flask backend application
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── config/               # Configuration files
│   │   ├── __init__.py
│   │   └── database.py       # Database configuration
│   ├── models/               # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user_model.py     # User model
│   │   ├── job_model.py      # Job model
│   │   └── resume_model.py   # Resume model
│   ├── routes/               # API route handlers
│   │   ├── __init__.py
│   │   ├── auth_routes.py    # Authentication routes
│   │   ├── job_routes.py     # Job management routes
│   │   └── resume_routes.py  # Resume handling routes
│   ├── services/             # Business logic services
│   │   └── __init__.py
│   ├── utils/                # Utility functions
│   │   └── __init__.py
│   ├── uploads/              # File upload storage
│   │   ├── resumes/         # Resume files
│   │   └── jds/             # Job description files
│   └── tests/                # Test files
│       └── __init__.py
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── hr/          # HR dashboard components
│   │   │   ├── candidate/   # Candidate dashboard components
│   │   │   └── common/      # Shared components
│   │   ├── pages/           # Page components
│   │   │   ├── LoginPage.jsx
│   │   │   └── RegisterPage.jsx
│   │   ├── context/         # React context
│   │   │   └── AuthContext.jsx
│   │   ├── services/        # API services
│   │   │   ├── api.js
│   │   │   └── auth.js
│   │   ├── utils/           # Utility functions
│   │   │   └── constants.js
│   │   ├── App.jsx          # Main App component
│   │   └── main.jsx         # Entry point
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
├── docs/                     # Documentation
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 💻 Usage

### 1. Register an Account
- Visit `http://localhost:5173/register`
- Choose your role: **HR** or **Candidate**
- Fill in your details and register

### 2. Login
- Visit `http://localhost:5173/login`
- Enter your credentials to access the dashboard

### 3. HR Workflow
1. **Create Jobs**: Use the "Create Job" button to post new positions
2. **Review Applications**: Monitor incoming resume submissions
3. **Manage Candidates**: Update application statuses and review matches
4. **View Analytics**: Track hiring metrics and performance

### 4. Candidate Workflow
1. **Browse Jobs**: Explore available job opportunities
2. **Apply to Jobs**: Submit resumes with AI-powered matching scores
3. **Track Applications**: Monitor your application status
4. **Manage Profile**: Update your skills and information

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Database
DATABASE_URL=sqlite:///resume_parser.db

# File Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# AI/ML Configuration
SPACY_MODEL=en_core_web_sm
```

### Frontend Environment Variables (.env.local)

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:5000/api
VITE_APP_TITLE=Resume Parser AI
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/

# Test specific endpoints
python test_api.py
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test

# Run end-to-end tests
npm run test:e2e
```

## 🚀 Deployment

### Backend Deployment (Heroku/Railway/DigitalOcean)

1. Configure production environment variables
2. Use PostgreSQL instead of SQLite for production
3. Set up proper logging and error handling
4. Configure CORS for production domain

### Frontend Deployment (Vercel/Netlify)

1. Build the application: `npm run build`
2. Configure environment variables on the platform
3. Set up proper routing for SPA
4. Configure API endpoints for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow Python PEP 8 style guide for backend code
- Use ESLint and Prettier for frontend code formatting
- Write comprehensive tests for new features
- Update documentation when adding new functionality
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **spaCy** - For natural language processing capabilities
- **React** - For the robust frontend framework
- **Flask** - For the lightweight backend framework
- **Tailwind CSS** - For beautiful and responsive design
- **Open Source Community** - For the amazing tools and libraries

## Support

For support, email kallappakabbur874@gmail.com.
Phone No : 6361664259

## 🔄 Changelog

### Version 1.0.0 (2025-12-20)
- Initial release
- Basic authentication system
- Job posting and management
- Resume upload and parsing
- AI-powered matching algorithm
- Role-based dashboards
- Responsive web design

---

