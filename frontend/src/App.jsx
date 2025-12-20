import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HRDashboard from './components/hr/HRDashboard';
import CandidateDashboard from './components/candidate/CandidateDashboard';

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    // Redirect based on actual user role
    if (user?.role === 'HR') {
      return <Navigate to="/hr/dashboard" replace />;
    } else {
      return <Navigate to="/candidate/dashboard" replace />;
    }
  }

  return children;
};

// Temporary Dashboard Components (we'll replace these with full dashboards)
// Main App Routes
const AppRoutes = () => {
  const { isAuthenticated, isHR, isCandidate } = useAuth();

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* Protected Routes - HR */}
      <Route 
        path="/hr/dashboard" 
        element={
          <ProtectedRoute requiredRole="HR">
            <HRDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Protected Routes - Candidate */}
      <Route 
        path="/candidate/dashboard" 
        element={
          <ProtectedRoute requiredRole="Candidate">
            <CandidateDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Home Route - Redirect based on auth status */}
      <Route 
        path="/" 
        element={
          isAuthenticated ? (
            isHR() ? (
              <Navigate to="/hr/dashboard" replace />
            ) : isCandidate() ? (
              <Navigate to="/candidate/dashboard" replace />
            ) : (
              <Navigate to="/login" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        } 
      />
      
      {/* Catch all - redirect to appropriate dashboard or login */}
      <Route 
        path="*" 
        element={
          <Navigate to={
            isAuthenticated ? (
              isHR() ? "/hr/dashboard" : "/candidate/dashboard"
            ) : "/login"
          } replace />
        } 
      />
    </Routes>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
