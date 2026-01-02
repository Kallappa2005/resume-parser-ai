import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import apiService from '../../services/api';
import CreateJobForm from './CreateJobForm';
import EditJobModal from './EditJobModal';
import JobAnalyticsModal from './JobAnalyticsModal';
import ViewApplicationsModal from './ViewApplicationsModal';

const HRDashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState({
    totalJobs: 0,
    totalApplications: 0,
    activeJobs: 0,
    archivedJobs: 0
  });
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateJob, setShowCreateJob] = useState(false);
  const [showViewApplications, setShowViewApplications] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [showEditJob, setShowEditJob] = useState(false);
  const [showJobAnalytics, setShowJobAnalytics] = useState(false);
  const [showArchivedJobs, setShowArchivedJobs] = useState(false);

  // Get recent active jobs (limit to 5 most recent)
  const displayJobs = showArchivedJobs 
    ? jobs.filter(job => job.archived_at) 
    : jobs.filter(job => !job.archived_at);
  const recentJobs = displayJobs.slice(0, 5);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [jobsResponse, resumesResponse] = await Promise.all([
        apiService.getJobs(true), // Include archived jobs for full stats
        apiService.getResumes()
      ]);
      
      const allJobs = jobsResponse.jobs || [];
      const resumes = resumesResponse.resumes || [];
      
      setJobs(allJobs);
      setStats({
        totalJobs: allJobs.length,
        activeJobs: jobsResponse.active_count || 0,
        archivedJobs: jobsResponse.archived_count || 0,
        totalApplications: resumes.length
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  const handleEditJob = (job) => {
    setSelectedJob(job);
    setShowEditJob(true);
  };

  const handleViewAnalytics = (job) => {
    setSelectedJob(job);
    setShowJobAnalytics(true);
  };

  const handleJobUpdated = () => {
    loadDashboardData();
    setShowEditJob(false);
    setSelectedJob(null);
  };

  const handleArchiveJob = async (jobId) => {
    try {
      await apiService.archiveJob(jobId);
      loadDashboardData();
    } catch (error) {
      console.error('Failed to archive job:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">HR Dashboard</h1>
              <p className="text-gray-600">Welcome back, {user?.name}!</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => setShowCreateJob(true)}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create Job
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 bg-blue-100 rounded-full">
                  <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Jobs</dt>
                  <dd className="text-3xl font-bold text-gray-900">{stats.totalJobs}</dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 bg-green-100 rounded-full">
                  <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Applications</dt>
                  <dd className="text-3xl font-bold text-gray-900">{stats.totalApplications}</dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 bg-yellow-100 rounded-full">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Jobs</dt>
                  <dd className="text-3xl font-bold text-gray-900">{stats.activeJobs}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Jobs */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                {showArchivedJobs ? 'Archived Jobs' : 'Recent Job Postings'}
              </h3>
              <div className="flex space-x-4">
                <span className="text-sm text-gray-500">
                  Showing {displayJobs.length} {showArchivedJobs ? 'archived' : 'active'} jobs
                </span>
                <button
                  onClick={() => setShowCreateJob(true)}
                  className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                >
                  {showArchivedJobs ? 'Create New Job' : 'View All'} →
                </button>
              </div>
            </div>
            
            {recentJobs.length === 0 ? (
              <div className="text-center py-8">
                <div className="flex justify-center mb-4">
                  <svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs posted yet</h3>
                <p className="text-gray-600 mb-4">Create your first job posting to start receiving applications.</p>
                <button
                  onClick={() => setShowCreateJob(true)}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                >
                  Create Your First Job
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {recentJobs.map((job) => (
                  <div key={job.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="text-lg font-medium text-gray-900">{job.title}</h4>
                        <p className="text-gray-600">{job.company}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          {job.location} • {job.experience_required}
                        </p>
                        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                          <span>Applications: {job.resumes_count || 0}</span>
                          <span>•</span>
                          <span>Views: {job.view_count || 0}</span>
                          <span>•</span>
                          <span>Status: {job.archived_at ? 'Archived' : 'Active'}</span>
                          {job.archived_at && (
                            <>
                              <span>•</span>
                              <span>Archived: {new Date(job.archived_at).toLocaleDateString()}</span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button 
                          onClick={() => {
                            setSelectedJob(job);
                            setShowViewApplications(true);
                          }}
                          className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                        >
                          Applications
                        </button>
                        <button 
                          onClick={() => handleEditJob(job)}
                          className="text-blue-600 hover:text-blue-500 text-sm font-medium"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => handleViewAnalytics(job)}
                          className="text-green-600 hover:text-green-500 text-sm font-medium"
                        >
                          Analytics
                        </button>
                        <button 
                          onClick={() => handleArchiveJob(job.id)}
                          className={job.archived_at ? "text-green-600 hover:text-green-500 text-sm font-medium" : "text-red-600 hover:text-red-500 text-sm font-medium"}
                        >
                          {job.archived_at ? 'Reactivate' : 'Archive'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setShowCreateJob(true)}>
            <div className="flex items-center">
              <div className="p-3 bg-indigo-100 rounded-full">
                <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">Create New Job</h3>
                <p className="text-gray-600">Post a new job opening</p>
              </div>
            </div>
          </div>

          <div 
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer" 
            onClick={() => setShowViewApplications(true)}
          >
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-full">
                <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">View Applications</h3>
                <p className="text-gray-600">Review candidate applications</p>
              </div>
            </div>
          </div>

          <div 
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer" 
            onClick={() => setShowArchivedJobs(!showArchivedJobs)}
          >
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-full">
                <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h8a2 2 0 002-2V8m-9 4h4" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {showArchivedJobs ? 'Hide' : 'Show'} Archived Jobs ({stats.archivedJobs})
                </h3>
                <p className="text-gray-600">
                  {showArchivedJobs ? 'Hide archived job postings' : 'View archived job postings'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* View Applications Modal */}
      {showViewApplications && (
        <ViewApplicationsModal
          onClose={() => {
            setShowViewApplications(false);
            setSelectedJob(null);
          }}
          selectedJob={selectedJob}
        />
      )}

      {/* Create Job Form Modal */}
      {showCreateJob && (
        <CreateJobForm
          onClose={() => setShowCreateJob(false)}
          onJobCreated={(newJob) => {
            // Refresh dashboard data after job creation
            loadDashboardData();
          }}
        />
      )}

      {/* Edit Job Modal */}
      {showEditJob && selectedJob && (
        <EditJobModal
          job={selectedJob}
          onClose={() => {
            setShowEditJob(false);
            setSelectedJob(null);
          }}
          onJobUpdated={handleJobUpdated}
        />
      )}

      {/* Job Analytics Modal */}
      {showJobAnalytics && selectedJob && (
        <JobAnalyticsModal
          job={selectedJob}
          onClose={() => {
            setShowJobAnalytics(false);
            setSelectedJob(null);
          }}
        />
      )}
    </div>
  );
};

export default HRDashboard;