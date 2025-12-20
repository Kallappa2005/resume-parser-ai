// API endpoints configuration
export const API_ENDPOINTS = {
  // Base URL
  BASE_URL: 'http://localhost:5000/api',
  
  // Authentication
  AUTH: {
    REGISTER: '/auth/register',
    LOGIN: '/auth/login',
    PROFILE: '/auth/profile',
    VERIFY_TOKEN: '/auth/verify-token',
  },
  
  // Jobs
  JOBS: {
    CREATE: '/jobs/create',
    LIST: '/jobs/list',
    DETAILS: (id) => `/jobs/${id}`,
    UPDATE: (id) => `/jobs/${id}`,
    DELETE: (id) => `/jobs/${id}`,
  },
  
  // Resumes
  RESUMES: {
    UPLOAD: '/resumes/upload',
    MY_APPLICATIONS: '/resumes/my-applications',
    JOB_RESUMES: (jobId) => `/resumes/job/${jobId}`,
    UPDATE_STATUS: (resumeId) => `/resumes/${resumeId}/status`,
    DETAILS: (resumeId) => `/resumes/${resumeId}`,
  },
  
  // Health
  HEALTH: '/health',
};

// User roles
export const USER_ROLES = {
  HR: 'HR',
  CANDIDATE: 'Candidate',
};

// Resume status options
export const RESUME_STATUS = {
  PENDING: 'pending',
  SHORTLISTED: 'shortlisted',
  REJECTED: 'rejected',
  HIRED: 'hired',
};

// File upload configuration
export const FILE_CONFIG = {
  MAX_SIZE: 16 * 1024 * 1024, // 16MB
  ALLOWED_TYPES: ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'],
  ALLOWED_EXTENSIONS: ['.pdf', '.docx', '.doc'],
};

// Navigation routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  HR_DASHBOARD: '/hr/dashboard',
  HR_JOBS: '/hr/jobs',
  HR_CREATE_JOB: '/hr/jobs/create',
  HR_JOB_DETAILS: '/hr/jobs/:id',
  HR_APPLICATIONS: '/hr/applications/:jobId',
  CANDIDATE_DASHBOARD: '/candidate/dashboard',
  CANDIDATE_JOBS: '/candidate/jobs',
  CANDIDATE_APPLICATIONS: '/candidate/applications',
  CANDIDATE_APPLY: '/candidate/apply/:jobId',
};

// Form validation patterns
export const VALIDATION = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD_MIN_LENGTH: 8,
  NAME_MIN_LENGTH: 2,
};

// Toast notification types
export const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};