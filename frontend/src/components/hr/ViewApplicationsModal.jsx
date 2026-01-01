import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import ApplicationDetailsModal from './ApplicationDetailsModal';

const ViewApplicationsModal = ({ onClose }) => {
  const [applications, setApplications] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState('all');
  const [loading, setLoading] = useState(true);
  const [updatingStatus, setUpdatingStatus] = useState(null);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [applicationsPerPage] = useState(3); // Show 3 applications per page

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [jobsResponse, applicationsResponse] = await Promise.all([
        apiService.getJobs(),
        apiService.getResumes()
      ]);
      
      setJobs(jobsResponse.jobs || []);
      setApplications(applicationsResponse.resumes || []);
    } catch (error) {
      console.error('Failed to load applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (resumeId, newStatus) => {
    setUpdatingStatus(resumeId);
    try {
      await apiService.updateResumeStatus(resumeId, { status: newStatus });
      
      // Update local state
      setApplications(prev => 
        prev.map(app => 
          app.id === resumeId ? { ...app, status: newStatus } : app
        )
      );
    } catch (error) {
      console.error('Failed to update status:', error);
      alert('Failed to update application status');
    } finally {
      setUpdatingStatus(null);
    }
  };

  const handleViewDetails = (application) => {
    setSelectedApplication(application);
    setShowDetailsModal(true);
  };

  const handleDownload = async (application) => {
    try {
      const blob = await apiService.downloadResume(application.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = application.filename || 'resume.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download resume:', error);
      alert('Failed to download resume');
    }
  };

  const onDetailsStatusUpdate = (resumeId, newStatus) => {
    // Update local state when status is updated from details modal
    setApplications(prev => 
      prev.map(app => 
        app.id === resumeId ? { ...app, status: newStatus } : app
      )
    );
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      shortlisted: 'bg-green-100 text-green-800 border-green-200',
      rejected: 'bg-red-100 text-red-800 border-red-200',
      hired: 'bg-blue-100 text-blue-800 border-blue-200'
    };
    
    return (
      <span className={`px-3 py-1 text-xs font-medium rounded-full border ${colors[status] || colors.pending}`}>
        {status || 'pending'}
      </span>
    );
  };

  const getMatchScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredApplications = selectedJob === 'all' 
    ? applications 
    : applications.filter(app => app.job_id === parseInt(selectedJob));

  // Pagination calculations
  const totalPages = Math.ceil(filteredApplications.length / applicationsPerPage);
  const indexOfLastApplication = currentPage * applicationsPerPage;
  const indexOfFirstApplication = indexOfLastApplication - applicationsPerPage;
  const currentApplications = filteredApplications.slice(indexOfFirstApplication, indexOfLastApplication);

  // Reset to first page when job filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedJob]);

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-center mt-4">Loading applications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">View Applications</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="px-6 py-4 bg-gray-50 border-b flex-shrink-0">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Filter by Job:</label>
            <select
              value={selectedJob}
              onChange={(e) => setSelectedJob(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Jobs ({applications.length})</option>
              {jobs.map(job => (
                <option key={job.id} value={job.id}>
                  {job.title} ({applications.filter(app => app.job_id === job.id).length})
                </option>
              ))}
            </select>
            <div className="ml-auto text-sm text-gray-600">
              Total Applications: {filteredApplications.length}
            </div>
          </div>
        </div>

        {/* Applications List */}
        <div className="flex-1 overflow-y-auto p-6 min-h-0">
          {filteredApplications.length === 0 ? (
            <div className="text-center py-12">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No applications found</h3>
              <p className="text-gray-600">No candidates have applied to {selectedJob === 'all' ? 'any jobs' : 'this job'} yet.</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 -m-6">
              {currentApplications.map((application) => {
                const job = jobs.find(j => j.id === application.job_id);
                const parsedData = application.parsed_data || {};
                
                return (
                  <div key={application.id} className="p-6 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-4 mb-2">
                          <h4 className="text-lg font-medium text-gray-900">
                            {application.candidate_name || 'Candidate'}
                          </h4>
                          {getStatusBadge(application.status)}
                          <div className="flex items-center">
                            <span className="text-sm text-gray-500 mr-2">Match:</span>
                            <span className={`font-medium ${getMatchScoreColor(application.match_score)}`}>
                              {application.match_score}%
                            </span>
                          </div>
                        </div>
                        
                        <div className="text-sm text-gray-600 space-y-1">
                          <p><strong>Applied for:</strong> {job?.title || 'Unknown Position'}</p>
                          <p><strong>Resume:</strong> {application.filename}</p>
                          <p><strong>Applied on:</strong> {new Date(application.uploaded_at).toLocaleDateString()}</p>
                          
                          {parsedData.skills && parsedData.skills.length > 0 && (
                            <div className="mt-2">
                              <p className="font-medium">Detected Skills:</p>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {parsedData.skills.slice(0, 10).map((skill, index) => (
                                  <span 
                                    key={index}
                                    className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                                  >
                                    {skill}
                                  </span>
                                ))}
                                {parsedData.skills.length > 10 && (
                                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                    +{parsedData.skills.length - 10} more
                                  </span>
                                )}
                              </div>
                            </div>
                          )}
                          
                          {parsedData.total_experience_years && (
                            <p><strong>Experience:</strong> {parsedData.total_experience_years} years</p>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="ml-6 flex flex-col space-y-2">
                        <select
                          value={application.status}
                          onChange={(e) => handleStatusUpdate(application.id, e.target.value)}
                          disabled={updatingStatus === application.id}
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="pending">Pending</option>
                          <option value="shortlisted">Shortlisted</option>
                          <option value="rejected">Rejected</option>
                          <option value="hired">Hired</option>
                        </select>
                        
                        <button 
                          onClick={() => handleViewDetails(application)}
                          className="px-4 py-2 text-sm text-indigo-600 hover:text-indigo-500 border border-indigo-200 rounded-md hover:bg-indigo-50"
                        >
                          View Details
                        </button>
                        
                        <button 
                          onClick={() => handleDownload(application)}
                          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-500 border border-gray-200 rounded-md hover:bg-gray-50"
                        >
                          Download Resume
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer with Pagination */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex-shrink-0">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              Showing {indexOfFirstApplication + 1}-{Math.min(indexOfLastApplication, filteredApplications.length)} of {filteredApplications.length} applications
            </div>
            
            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={handlePrevPage}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                
                <div className="flex items-center space-x-1">
                  {[...Array(totalPages)].map((_, index) => {
                    const pageNumber = index + 1;
                    return (
                      <button
                        key={pageNumber}
                        onClick={() => handlePageChange(pageNumber)}
                        className={`px-3 py-1 text-sm font-medium rounded-md ${
                          currentPage === pageNumber
                            ? 'bg-indigo-600 text-white'
                            : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {pageNumber}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  onClick={handleNextPage}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
            
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
            >
              Close
            </button>
          </div>
        </div>
      </div>

      {/* Application Details Modal */}
      {showDetailsModal && selectedApplication && (
        <ApplicationDetailsModal
          application={selectedApplication}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedApplication(null);
          }}
          onStatusUpdate={onDetailsStatusUpdate}
        />
      )}
    </div>
  );
};

export default ViewApplicationsModal;