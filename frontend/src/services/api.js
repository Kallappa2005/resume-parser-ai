// API Configuration and Base Setup
const API_BASE_URL = 'http://localhost:5000/api';

// API utility class for handling all backend communication
class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Get authorization header
  getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // Generic API request handler
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      ...this.getAuthHeader(),
    };

    const config = {
      headers: defaultHeaders,
      ...options,
    };

    // Handle FormData (for file uploads)
    if (options.body instanceof FormData) {
      delete config.headers['Content-Type']; // Let browser set it
    }

    try {
      const response = await fetch(url, config);
      
      // Check if response is ok
      if (!response.ok) {
        const error = await response.json().catch(() => ({ 
          error: `HTTP ${response.status}: ${response.statusText}` 
        }));
        throw new Error(error.error || error.message || 'Request failed');
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return await response.text();
    } catch (error) {
      console.error(`API Request failed: ${options.method || 'GET'} ${endpoint}`, error);
      throw error;
    }
  }

  // Authentication APIs
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async getProfile() {
    return this.request('/auth/profile', {
      method: 'GET',
    });
  }

  async verifyToken() {
    return this.request('/auth/verify-token', {
      method: 'POST',
    });
  }

  // Job APIs
  async createJob(jobData) {
    return this.request('/jobs/create', {
      method: 'POST',
      body: JSON.stringify(jobData),
    });
  }

  async updateJob(jobId, jobData) {
    return this.request(`/jobs/${jobId}`, {
      method: 'PUT',
      body: JSON.stringify(jobData),
    });
  }

  async archiveJob(jobId) {
    return this.request(`/jobs/${jobId}/archive`, {
      method: 'PUT',
    });
  }

  async getJobAnalytics(jobId) {
    return this.request(`/jobs/${jobId}/analytics`, {
      method: 'GET',
    });
  }

  async getJobDetails(jobId) {
    return this.request(`/jobs/${jobId}`, {
      method: 'GET',
    });
  }

  async getJobs(includeArchived = false) {
    const params = includeArchived ? '?include_archived=true' : '';
    return this.request(`/jobs/list${params}`, {
      method: 'GET',
    });
  }

  // Resume APIs
  async uploadResume(formData) {
    return this.request('/resumes/upload', {
      method: 'POST',
      body: formData, // FormData object
    });
  }

  async getMyApplications() {
    return this.request('/resumes/my-applications', {
      method: 'GET',
    });
  }

  async getResumes(filters = {}) {
    // Build query string from filters
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value.toString());
      }
    });
    
    const queryString = params.toString();
    const endpoint = queryString ? `/resumes/list?${queryString}` : '/resumes/list';
    
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  async getJobResumes(jobId) {
    return this.request(`/resumes/job/${jobId}`, {
      method: 'GET',
    });
  }

  async updateResumeStatus(resumeId, statusData) {
    return this.request(`/resumes/${resumeId}/status`, {
      method: 'PUT',
      body: JSON.stringify(statusData),
    });
  }

  async getResumeDetails(resumeId) {
    return this.request(`/resumes/${resumeId}`, {
      method: 'GET',
    });
  }

  async downloadResume(resumeId) {
    const response = await fetch(`${this.baseURL}/resumes/${resumeId}/download`, {
      method: 'GET',
      headers: this.getAuthHeader()
    });
    
    if (!response.ok) {
      throw new Error('Failed to download resume');
    }
    
    return response.blob();
  }

  async toggleShortlist(resumeId) {
    return this.request(`/resumes/${resumeId}/shortlist`, {
      method: 'PUT',
    });
  }

  async compareResumes(resumeIds) {
    return this.request('/resumes/compare', {
      method: 'POST',
      body: JSON.stringify({ resume_ids: resumeIds }),
    });
  }

  async getRankedCandidates(jobId, options = {}) {
    const params = new URLSearchParams();
    if (options.limit) params.append('limit', options.limit);
    if (options.status && options.status !== 'all') params.append('status', options.status);
    if (options.min_score) params.append('min_score', options.min_score);
    
    const queryString = params.toString();
    const endpoint = queryString ? `/resumes/job/${jobId}/ranked?${queryString}` : `/resumes/job/${jobId}/ranked`;
    
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health', {
      method: 'GET',
    });
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;