#!/usr/bin/env python3
"""
API Test Script for Resume Parser Application
Run this script to test all API endpoints systematically.
"""

import requests
import json
import os
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:5000/api"
TEST_DATA_DIR = "test_data"

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.tokens = {}
        self.test_users = {}
        self.test_jobs = {}
        
    def log(self, message, status="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        
    def test_endpoint(self, method, endpoint, data=None, headers=None, files=None):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(url, data=data, files=files, headers=headers)
                else:
                    response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
                
            self.log(f"{method} {endpoint} - Status: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.status_code, response.json()
            else:
                return response.status_code, response.text
                
        except requests.exceptions.ConnectionError:
            self.log("❌ Connection failed. Make sure Flask server is running!", "ERROR")
            return None, None
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "ERROR")
            return None, None
    
    def test_health_check(self):
        """Test health endpoint"""
        self.log("🏥 Testing Health Check...")
        status, data = self.test_endpoint("GET", "/health")
        
        if status == 200:
            self.log("✅ Health check passed")
            print(f"   Response: {data}")
            return True
        else:
            self.log("❌ Health check failed")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        self.log("👤 Testing User Registration...")
        
        # Test HR registration
        hr_data = {
            "name": "HR Manager",
            "email": "hr@test.com",
            "password": "password123",
            "role": "HR"
        }
        
        status, data = self.test_endpoint("POST", "/auth/register", hr_data)
        
        if status == 201:
            self.log("✅ HR registration successful")
            self.tokens['hr'] = data.get('access_token')
            self.test_users['hr'] = data.get('user')
            print(f"   HR Token: {self.tokens['hr'][:50]}...")
        else:
            self.log("❌ HR registration failed")
            print(f"   Error: {data}")
            
        # Test Candidate registration
        candidate_data = {
            "name": "John Candidate",
            "email": "candidate@test.com",
            "password": "password123",
            "role": "Candidate"
        }
        
        status, data = self.test_endpoint("POST", "/auth/register", candidate_data)
        
        if status == 201:
            self.log("✅ Candidate registration successful")
            self.tokens['candidate'] = data.get('access_token')
            self.test_users['candidate'] = data.get('user')
            print(f"   Candidate Token: {self.tokens['candidate'][:50]}...")
        else:
            self.log("❌ Candidate registration failed")
            print(f"   Error: {data}")
    
    def test_user_login(self):
        """Test user login"""
        self.log("🔐 Testing User Login...")
        
        # Test HR login
        login_data = {
            "email": "hr@test.com",
            "password": "password123"
        }
        
        status, data = self.test_endpoint("POST", "/auth/login", login_data)
        
        if status == 200:
            self.log("✅ HR login successful")
            self.tokens['hr_login'] = data.get('access_token')
            print(f"   Login Token: {self.tokens['hr_login'][:50]}...")
        else:
            self.log("❌ HR login failed")
            print(f"   Error: {data}")
    
    def test_job_creation(self):
        """Test job creation"""
        self.log("💼 Testing Job Creation...")
        
        if 'hr' not in self.tokens:
            self.log("❌ No HR token available for job creation")
            return
            
        headers = {"Authorization": f"Bearer {self.tokens['hr']}"}
        
        job_data = {
            "title": "Senior Python Developer",
            "description_text": "We are looking for an experienced Python developer with expertise in Flask, Django, and machine learning frameworks. Must have 3+ years of experience in backend development.",
            "company": "TechCorp Solutions",
            "experience_required": "3-5 years",
            "location": "Remote",
            "salary_range": "$80,000 - $120,000"
        }
        
        status, data = self.test_endpoint("POST", "/jobs/create", job_data, headers)
        
        if status == 201:
            self.log("✅ Job creation successful")
            self.test_jobs['python_dev'] = data.get('job')
            print(f"   Job ID: {data.get('job', {}).get('id')}")
            print(f"   Job Title: {data.get('job', {}).get('title')}")
        else:
            self.log("❌ Job creation failed")
            print(f"   Error: {data}")
    
    def test_job_listing(self):
        """Test job listing"""
        self.log("📋 Testing Job Listing...")
        
        # Test HR job listing
        if 'hr' in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['hr']}"}
            status, data = self.test_endpoint("GET", "/jobs/list", headers=headers)
            
            if status == 200:
                self.log("✅ HR job listing successful")
                jobs = data.get('jobs', [])
                print(f"   Found {len(jobs)} jobs for HR")
                for job in jobs:
                    print(f"   - {job.get('title')} ({job.get('company')})")
            else:
                self.log("❌ HR job listing failed")
                print(f"   Error: {data}")
        
        # Test Candidate job listing
        if 'candidate' in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['candidate']}"}
            status, data = self.test_endpoint("GET", "/jobs/list", headers=headers)
            
            if status == 200:
                self.log("✅ Candidate job listing successful")
                jobs = data.get('jobs', [])
                print(f"   Candidate sees {len(jobs)} available jobs")
            else:
                self.log("❌ Candidate job listing failed")
                print(f"   Error: {data}")
    
    def test_profile_access(self):
        """Test profile access"""
        self.log("👨‍💼 Testing Profile Access...")
        
        for role in ['hr', 'candidate']:
            if role in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens[role]}"}
                status, data = self.test_endpoint("GET", "/auth/profile", headers=headers)
                
                if status == 200:
                    self.log(f"✅ {role.upper()} profile access successful")
                    user = data.get('user', {})
                    print(f"   {role.upper()}: {user.get('name')} ({user.get('email')})")
                else:
                    self.log(f"❌ {role.upper()} profile access failed")
                    print(f"   Error: {data}")
    
    def test_token_verification(self):
        """Test token verification"""
        self.log("🔍 Testing Token Verification...")
        
        for role in ['hr', 'candidate']:
            if role in self.tokens:
                headers = {"Authorization": f"Bearer {self.tokens[role]}"}
                status, data = self.test_endpoint("POST", "/auth/verify-token", headers=headers)
                
                if status == 200:
                    self.log(f"✅ {role.upper()} token verification successful")
                else:
                    self.log(f"❌ {role.upper()} token verification failed")
                    print(f"   Error: {data}")
    
    def create_test_resume_file(self):
        """Create a test resume file"""
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
        resume_content = """
John Candidate
Software Engineer

Email: candidate@test.com
Phone: +1-234-567-8900

EXPERIENCE:
- 3 years of Python development
- Flask and Django frameworks
- Machine Learning with scikit-learn
- Database design with PostgreSQL

SKILLS:
Python, JavaScript, React, Flask, Django, PostgreSQL, Git, Docker

EDUCATION:
Bachelor of Science in Computer Science
University of Technology, 2020
        """
        
        resume_path = os.path.join(TEST_DATA_DIR, "test_resume.txt")
        with open(resume_path, 'w') as f:
            f.write(resume_content)
        
        return resume_path
    
    def test_resume_upload(self):
        """Test resume upload"""
        self.log("📄 Testing Resume Upload...")
        
        if 'candidate' not in self.tokens or not self.test_jobs.get('python_dev'):
            self.log("❌ Missing candidate token or job for resume upload")
            return
        
        # Create test resume file
        resume_path = self.create_test_resume_file()
        
        headers = {"Authorization": f"Bearer {self.tokens['candidate']}"}
        job_id = self.test_jobs['python_dev'].get('id')
        
        with open(resume_path, 'rb') as f:
            files = {'resume': ('test_resume.txt', f, 'text/plain')}
            data = {'job_id': str(job_id)}
            
            status, response = self.test_endpoint("POST", "/resumes/upload", 
                                                data=data, headers=headers, files=files)
        
        if status == 201:
            self.log("✅ Resume upload successful")
            print(f"   Resume ID: {response.get('resume', {}).get('id')}")
        else:
            self.log("❌ Resume upload failed")
            print(f"   Error: {response}")
        
        # Cleanup
        if os.path.exists(resume_path):
            os.remove(resume_path)
    
    def test_candidate_applications(self):
        """Test candidate applications listing"""
        self.log("📋 Testing Candidate Applications...")
        
        if 'candidate' not in self.tokens:
            self.log("❌ No candidate token available")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens['candidate']}"}
        status, data = self.test_endpoint("GET", "/resumes/my-applications", headers=headers)
        
        if status == 200:
            self.log("✅ Candidate applications listing successful")
            applications = data.get('applications', [])
            print(f"   Found {len(applications)} applications")
            for app in applications:
                print(f"   - {app.get('filename')} -> {app.get('job', {}).get('title')}")
        else:
            self.log("❌ Candidate applications listing failed")
            print(f"   Error: {data}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 60)
        print("🚀 RESUME PARSER API TEST SUITE")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            self.log("❌ Health check failed. Make sure Flask server is running!")
            return
        
        print("\n" + "=" * 40)
        print("AUTHENTICATION TESTS")
        print("=" * 40)
        
        self.test_user_registration()
        self.test_user_login()
        self.test_profile_access()
        self.test_token_verification()
        
        print("\n" + "=" * 40)
        print("JOB MANAGEMENT TESTS")
        print("=" * 40)
        
        self.test_job_creation()
        self.test_job_listing()
        
        print("\n" + "=" * 40)
        print("RESUME MANAGEMENT TESTS")
        print("=" * 40)
        
        self.test_resume_upload()
        self.test_candidate_applications()
        
        print("\n" + "=" * 60)
        print("🏁 TEST SUITE COMPLETED")
        print("=" * 60)
        
        # Summary
        print("\n📊 TOKEN SUMMARY:")
        for role, token in self.tokens.items():
            if token:
                print(f"   {role.upper()}: {token[:30]}...")
        
        print("\n📋 JOB SUMMARY:")
        for job_key, job_data in self.test_jobs.items():
            if job_data:
                print(f"   {job_key}: {job_data.get('title')} (ID: {job_data.get('id')})")

if __name__ == "__main__":
    print("Starting API Test Suite...")
    print("Make sure the Flask server is running on http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    try:
        tester = APITester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n❌ Test suite interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {str(e)}")
    
    print("\n👋 Test suite finished!")