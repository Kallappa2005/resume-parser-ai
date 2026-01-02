import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import ApplicationDetailsModal from './ApplicationDetailsModal';
import ResumesComparisonModal from './ResumesComparisonModal';

const ViewApplicationsModal = ({ onClose, selectedJob }) => {
  const [applications, setApplications] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(selectedJob?.id || 'all');
  const [loading, setLoading] = useState(true);
  const [updatingStatus, setUpdatingStatus] = useState(null);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  
  // Advanced Search and Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [minMatchScore, setMinMatchScore] = useState('');
  const [maxMatchScore, setMaxMatchScore] = useState('');
  const [minExperience, setMinExperience] = useState('');
  const [maxExperience, setMaxExperience] = useState('');
  const [quickFilter, setQuickFilter] = useState('');
  const [sortBy, setSortBy] = useState('uploaded_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  
  // Ranking and Comparison State
  const [viewMode, setViewMode] = useState('list'); // 'list', 'ranking', 'comparison'
  const [selectedForComparison, setSelectedForComparison] = useState([]);
  const [rankedCandidates, setRankedCandidates] = useState([]);
  const [loadingRanking, setLoadingRanking] = useState(false);
  const [showComparisonModal, setShowComparisonModal] = useState(false);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [applicationsPerPage] = useState(3); // Show 3 applications per page

  useEffect(() => {
    loadData();
  }, []);
  
  // Reload data when filters change
  useEffect(() => {
    if (viewMode === 'list') {
      loadData();
    } else if (viewMode === 'ranking' && selectedJobId !== 'all') {
      loadRankedData();
    }
    setCurrentPage(1); // Reset to first page when filters change
  }, [searchQuery, statusFilter, selectedJobId, minMatchScore, maxMatchScore, minExperience, maxExperience, quickFilter, sortBy, sortOrder, viewMode]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Build filters object
      const filters = {};
      if (searchQuery) filters.search = searchQuery;
      if (statusFilter !== 'all') filters.status = statusFilter;
      if (selectedJobId !== 'all') filters.job_id = selectedJobId;
      if (minMatchScore) filters.min_match_score = parseFloat(minMatchScore);
      if (maxMatchScore) filters.max_match_score = parseFloat(maxMatchScore);
      if (minExperience) filters.min_experience = parseInt(minExperience);
      if (maxExperience) filters.max_experience = parseInt(maxExperience);
      if (quickFilter) filters.quick_filter = quickFilter;
      if (sortBy) filters.sort_by = sortBy;
      if (sortOrder) filters.sort_order = sortOrder;
      
      const [jobsResponse, applicationsResponse] = await Promise.all([
        apiService.getJobs(),
        apiService.getResumes(filters)
      ]);
      
      setJobs(jobsResponse.jobs || []);
      setApplications(applicationsResponse.resumes || []);
    } catch (error) {
      console.error('Failed to load applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRankedData = async () => {
    if (selectedJobId === 'all') {
      setRankedCandidates([]);
      return;
    }

    try {
      setLoadingRanking(true);
      const options = {};
      if (statusFilter !== 'all') options.status = statusFilter;
      if (minMatchScore) options.min_score = parseFloat(minMatchScore);
      
      const response = await apiService.getRankedCandidates(selectedJobId, options);
      setRankedCandidates(response.candidates || []);
    } catch (error) {
      console.error('Failed to load ranked candidates:', error);
    } finally {
      setLoadingRanking(false);
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
      
      // Update ranked candidates if in ranking view
      if (viewMode === 'ranking') {
        setRankedCandidates(prev => 
          prev.map(candidate => 
            candidate.id === resumeId ? { ...candidate, status: newStatus } : candidate
          )
        );
      }
    } catch (error) {
      console.error('Failed to update status:', error);
      alert('Failed to update application status');
    } finally {
      setUpdatingStatus(null);
    }
  };

  const handleToggleShortlist = async (resumeId) => {
    setUpdatingStatus(resumeId);
    try {
      const response = await apiService.toggleShortlist(resumeId);
      
      // Update local state
      setApplications(prev => 
        prev.map(app => 
          app.id === resumeId ? { ...app, status: response.status } : app
        )
      );
      
      // Update ranked candidates if in ranking view
      if (viewMode === 'ranking') {
        setRankedCandidates(prev => 
          prev.map(candidate => 
            candidate.id === resumeId ? { ...candidate, status: response.status } : candidate
          )
        );
      }
    } catch (error) {
      console.error('Failed to toggle shortlist:', error);
      alert('Failed to update shortlist status');
    } finally {
      setUpdatingStatus(null);
    }
  };

  const handleSelectForComparison = (resumeId) => {
    setSelectedForComparison(prev => {
      if (prev.includes(resumeId)) {
        return prev.filter(id => id !== resumeId);
      } else if (prev.length < 5) { // Maximum 5 for comparison
        return [...prev, resumeId];
      } else {
        alert('You can compare maximum 5 candidates at once');
        return prev;
      }
    });
  };

  const handleStartComparison = () => {
    if (selectedForComparison.length < 2) {
      alert('Please select at least 2 candidates for comparison');
      return;
    }
    setShowComparisonModal(true);
  };

  const handleClearComparison = () => {
    setSelectedForComparison([]);
    setViewMode('list');
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

  const filteredApplications = applications; // Filtering is now done on backend

  // Pagination calculations
  const totalPages = Math.ceil(filteredApplications.length / applicationsPerPage);
  const indexOfLastApplication = currentPage * applicationsPerPage;
  const indexOfFirstApplication = indexOfLastApplication - applicationsPerPage;
  const currentApplications = filteredApplications.slice(indexOfFirstApplication, indexOfLastApplication);

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
  };
  
  // Search and filter handlers
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };
  
  const handleQuickFilter = (filterType) => {
    setQuickFilter(quickFilter === filterType ? '' : filterType);
  };
  
  const clearAllFilters = () => {
    setSearchQuery('');
    setStatusFilter('all');
    setSelectedJobId('all');
    setMinMatchScore('');
    setMaxMatchScore('');
    setMinExperience('');
    setMaxExperience('');
    setQuickFilter('');
    setSortBy('uploaded_at');
    setSortOrder('desc');
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
          
          {/* View Mode Controls */}
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 text-sm font-medium rounded-md ${
                  viewMode === 'list'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                📋 List View
              </button>
              <button
                onClick={() => setViewMode('ranking')}
                disabled={selectedJobId === 'all'}
                className={`px-4 py-2 text-sm font-medium rounded-md ${
                  viewMode === 'ranking'
                    ? 'bg-indigo-600 text-white'
                    : selectedJobId === 'all'
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                🏆 Ranking View
              </button>
              <button
                onClick={handleStartComparison}
                disabled={selectedForComparison.length < 2}
                className={`px-4 py-2 text-sm font-medium rounded-md ${
                  viewMode === 'comparison'
                    ? 'bg-indigo-600 text-white'
                    : selectedForComparison.length < 2
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                ⚖️ Compare ({selectedForComparison.length}/5)
              </button>
            </div>
            
            {selectedForComparison.length > 0 && (
              <button
                onClick={handleClearComparison}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Clear Selection
              </button>
            )}
          </div>
        </div>

        {/* Advanced Search and Filters */}
        <div className="border-b bg-gray-50 flex-shrink-0">
          {/* Search Bar and Quick Actions */}
          <div className="px-6 py-4">
            <div className="flex flex-wrap items-center gap-4">
              {/* Search Input */}
              <div className="flex-1 min-w-64">
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={handleSearchChange}
                    placeholder="Search by name, skills, job title, or education..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>

              {/* Quick Filter Buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleQuickFilter('top_candidates')}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    quickFilter === 'top_candidates'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  ⭐ Top Candidates
                </button>
                <button
                  onClick={() => handleQuickFilter('recent_applications')}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    quickFilter === 'recent_applications'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  🕒 Recent
                </button>
                <button
                  onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                  className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  🔧 Filters
                </button>
                <button
                  onClick={clearAllFilters}
                  className="px-3 py-2 text-sm font-medium text-red-600 bg-white border border-red-300 rounded-md hover:bg-red-50"
                >
                  Clear All
                </button>
              </div>
            </div>
          </div>

          {/* Advanced Filters Panel */}
          {showAdvancedFilters && (
            <div className="px-6 py-4 bg-white border-t">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Job Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Job Position</label>
                  <select
                    value={selectedJobId}
                    onChange={(e) => setSelectedJobId(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  >
                    <option value="all">All Jobs ({applications.length})</option>
                    {jobs.map((job) => (
                      <option key={job.id} value={job.id}>
                        {job.title}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Status Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  >
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="shortlisted">Shortlisted</option>
                    <option value="rejected">Rejected</option>
                    <option value="hired">Hired</option>
                  </select>
                </div>

                {/* Match Score Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Match Score (%)</label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="number"
                      value={minMatchScore}
                      onChange={(e) => setMinMatchScore(e.target.value)}
                      placeholder="Min"
                      min="0"
                      max="100"
                      className="w-full px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                    />
                    <span className="text-gray-500">-</span>
                    <input
                      type="number"
                      value={maxMatchScore}
                      onChange={(e) => setMaxMatchScore(e.target.value)}
                      placeholder="Max"
                      min="0"
                      max="100"
                      className="w-full px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                    />
                  </div>
                </div>

                {/* Experience Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Experience (Years)</label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="number"
                      value={minExperience}
                      onChange={(e) => setMinExperience(e.target.value)}
                      placeholder="Min"
                      min="0"
                      className="w-full px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                    />
                    <span className="text-gray-500">-</span>
                    <input
                      type="number"
                      value={maxExperience}
                      onChange={(e) => setMaxExperience(e.target.value)}
                      placeholder="Max"
                      min="0"
                      className="w-full px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                    />
                  </div>
                </div>

                {/* Sort Options */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
                  <div className="flex items-center space-x-2">
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="flex-1 px-2 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                    >
                      <option value="uploaded_at">Date Applied</option>
                      <option value="match_score">Match Score</option>
                      <option value="candidate_name">Name</option>
                      <option value="experience">Experience</option>
                    </select>
                    <button
                      onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                      className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 text-sm"
                    >
                      {sortOrder === 'asc' ? '↑' : '↓'}
                    </button>
                  </div>
                </div>

                {/* Results Count */}
                <div className="md:col-span-2 lg:col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Results</label>
                  <div className="px-3 py-2 bg-gray-100 border border-gray-300 rounded-md text-sm text-gray-600">
                    {filteredApplications.length} applications found
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Applications List or Ranking View */}
        <div className="flex-1 overflow-y-auto p-6 min-h-0">
          {viewMode === 'ranking' ? (
            // Ranking View
            <div>
              {loadingRanking ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading candidate rankings...</p>
                </div>
              ) : rankedCandidates.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No candidates to rank</h3>
                  <p className="text-gray-600">Select a specific job to view ranked candidates.</p>
                </div>
              ) : (
                <div>
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">🏆 Candidate Rankings</h4>
                    <p className="text-sm text-gray-600">
                      Candidates ranked by AI match score (Skills 60% + Experience 30% + Education 10%)
                    </p>
                  </div>
                  
                  <div className="space-y-4">
                    {rankedCandidates.map((candidate, index) => (
                      <div key={candidate.id} className={`bg-white border-2 rounded-lg p-4 ${
                        index === 0 ? 'border-yellow-400 bg-yellow-50' :
                        index === 1 ? 'border-gray-300 bg-gray-50' :
                        index === 2 ? 'border-yellow-600 bg-yellow-25' :
                        'border-gray-200'
                      }`}>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center space-x-4">
                            {/* Rank Badge */}
                            <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg ${
                              index === 0 ? 'bg-yellow-500' :
                              index === 1 ? 'bg-gray-400' :
                              index === 2 ? 'bg-yellow-600' :
                              'bg-gray-300 text-gray-600'
                            }`}>
                              {index < 3 ? ['🥇', '🥈', '🥉'][index] : candidate.rank}
                            </div>
                            
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <h5 className="text-lg font-semibold text-gray-900">
                                  {candidate.candidate_name}
                                </h5>
                                <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                                  candidate.match_score >= 80 ? 'bg-green-100 text-green-800' :
                                  candidate.match_score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {Math.round(candidate.match_score)}% match
                                </span>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  candidate.status === 'shortlisted' ? 'bg-yellow-100 text-yellow-800' :
                                  candidate.status === 'pending' ? 'bg-blue-100 text-blue-800' :
                                  candidate.status === 'rejected' ? 'bg-red-100 text-red-800' :
                                  'bg-green-100 text-green-800'
                                }`}>
                                  {candidate.status.charAt(0).toUpperCase() + candidate.status.slice(1)}
                                </span>
                              </div>
                              
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                                <div>
                                  <span className="font-medium">Experience:</span>
                                  <br />
                                  <span>{candidate.experience_years} years</span>
                                </div>
                                <div>
                                  <span className="font-medium">Education:</span>
                                  <br />
                                  <span>{candidate.education_level}</span>
                                </div>
                                <div>
                                  <span className="font-medium">Skills Match:</span>
                                  <br />
                                  <span>{candidate.matched_skills_count}/{candidate.total_skills_count} skills</span>
                                </div>
                                <div>
                                  <span className="font-medium">Applied:</span>
                                  <br />
                                  <span>{new Date(candidate.uploaded_at).toLocaleDateString()}</span>
                                </div>
                              </div>
                              
                              {/* Top Skills */}
                              {candidate.top_skills.length > 0 && (
                                <div className="mt-3">
                                  <span className="text-sm font-medium text-gray-700">Top Skills: </span>
                                  <div className="inline-flex flex-wrap gap-1 mt-1">
                                    {candidate.top_skills.map((skill, skillIndex) => (
                                      <span key={skillIndex} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                        {skill}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          {/* Actions for Ranked View */}
                          <div className="flex flex-col space-y-2 ml-4">
                            <input
                              type="checkbox"
                              checked={selectedForComparison.includes(candidate.id)}
                              onChange={() => handleSelectForComparison(candidate.id)}
                              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                              title="Select for comparison"
                            />
                            <button
                              onClick={() => handleToggleShortlist(candidate.id)}
                              disabled={updatingStatus === candidate.id}
                              className={`px-2 py-1 text-xs rounded ${
                                candidate.status === 'shortlisted'
                                  ? 'bg-yellow-200 text-yellow-800 hover:bg-yellow-300'
                                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                              }`}
                              title={candidate.status === 'shortlisted' ? 'Remove from shortlist' : 'Add to shortlist'}
                            >
                              {candidate.status === 'shortlisted' ? '⭐' : '☆'}
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            // List View
            <>
              {filteredApplications.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No applications found</h3>
                  <p className="text-gray-600">No candidates have applied to {selectedJobId === 'all' ? 'any jobs' : 'this job'} yet.</p>
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
                        {/* Comparison Checkbox */}
                        <label className="flex items-center space-x-2 text-sm">
                          <input
                            type="checkbox"
                            checked={selectedForComparison.includes(application.id)}
                            onChange={() => handleSelectForComparison(application.id)}
                            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                          />
                          <span className="text-gray-700">Compare</span>
                        </label>

                        {/* Shortlist Toggle */}
                        <button
                          onClick={() => handleToggleShortlist(application.id)}
                          disabled={updatingStatus === application.id}
                          className={`px-3 py-1 text-xs font-medium rounded-full ${
                            application.status === 'shortlisted'
                              ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {application.status === 'shortlisted' ? '⭐ Shortlisted' : '☆ Shortlist'}
                        </button>

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
            </>
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

      {/* Resumes Comparison Modal */}
      {showComparisonModal && selectedForComparison.length >= 2 && (
        <ResumesComparisonModal
          resumeIds={selectedForComparison}
          onClose={() => setShowComparisonModal(false)}
        />
      )}
    </div>
  );
};

export default ViewApplicationsModal;