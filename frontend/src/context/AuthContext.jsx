import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/auth';

// Create authentication context
const AuthContext = createContext();

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Authentication provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setLoading(true);
      
      // Check if user is already logged in
      if (authService.isAuthenticated()) {
        const currentUser = authService.getCurrentUser();
        
        // Verify token with backend
        try {
          await authService.verifyToken();
          setUser(currentUser);
        } catch (error) {
          // Token is invalid, clear auth data
          authService.logout();
          setUser(null);
        }
      }
    } catch (error) {
      console.error('Auth initialization failed:', error);
      setError('Failed to initialize authentication');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await authService.login(email, password);
      setUser(response.user);
      
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await authService.register(userData);
      // Don't auto-login after registration - let user login manually
      // setUser(response.user);
      
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setError(null);
  };

  const refreshProfile = async () => {
    try {
      const updatedUser = await authService.getProfile();
      setUser(updatedUser);
      return updatedUser;
    } catch (error) {
      console.error('Failed to refresh profile:', error);
      throw error;
    }
  };

  const clearError = () => {
    setError(null);
  };

  // Check user role
  const isHR = () => user?.role === 'HR';
  const isCandidate = () => user?.role === 'Candidate';

  const value = {
    // State
    user,
    loading,
    error,
    
    // Actions
    login,
    register,
    logout,
    refreshProfile,
    clearError,
    
    // Utilities
    isAuthenticated: !!user,
    isHR,
    isCandidate,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};