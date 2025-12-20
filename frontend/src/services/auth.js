import apiService from './api';

// Authentication service with token management
class AuthService {
  // Login user and store token
  async login(email, password) {
    try {
      const response = await apiService.login({ email, password });
      
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        return response;
      }
      
      throw new Error('No access token received');
    } catch (error) {
      throw error;
    }
  }

  // Register new user
  async register(userData) {
    try {
      const response = await apiService.register(userData);
      
      // Don't store token automatically - let user login manually
      // if (response.access_token) {
      //   localStorage.setItem('access_token', response.access_token);
      //   localStorage.setItem('user', JSON.stringify(response.user));
      //   return response;
      // }
      
      return response;
    } catch (error) {
      throw error;
    }
  }

  // Logout user
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  // Get current user from localStorage
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  // Get stored token
  getToken() {
    return localStorage.getItem('access_token');
  }

  // Check if user is authenticated
  isAuthenticated() {
    const token = this.getToken();
    const user = this.getCurrentUser();
    return !!(token && user);
  }

  // Check if user has specific role
  hasRole(role) {
    const user = this.getCurrentUser();
    return user && user.role === role;
  }

  // Verify token with backend
  async verifyToken() {
    try {
      const response = await apiService.verifyToken();
      return response;
    } catch (error) {
      // If token is invalid, clear stored data
      this.logout();
      throw error;
    }
  }

  // Get fresh user profile
  async getProfile() {
    try {
      const response = await apiService.getProfile();
      
      if (response.user) {
        localStorage.setItem('user', JSON.stringify(response.user));
        return response.user;
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  }
}

// Create and export singleton instance
const authService = new AuthService();
export default authService;