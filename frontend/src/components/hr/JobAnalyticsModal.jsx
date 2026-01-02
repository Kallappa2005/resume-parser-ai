import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';

const JobAnalyticsModal = ({ job, onClose }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (job?.id) {
      loadAnalytics();
    }
  }, [job?.id]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await apiService.getJobAnalytics(job.id);
      setAnalytics(response);
    } catch (error) {
      setError(error.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      shortlisted: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      hired: 'bg-blue-100 text-blue-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-center mt-4">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Analytics - {job?.title}</h3>
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

        <div className="p-6">
          {error ? (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.68-.833-2.45 0L3.372 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">{error}</h3>
                </div>
              </div>
            </div>
          ) : analytics ? (
            <div className="space-y-8">
              {/* Overview Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-blue-50 rounded-lg p-6">
                  <div className="flex items-center">
                    <div className="p-3 bg-blue-100 rounded-full">
                      <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-blue-600">Total Views</p>
                      <p className="text-2xl font-semibold text-blue-900">{analytics.total_views}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 rounded-lg p-6">
                  <div className="flex items-center">
                    <div className="p-3 bg-green-100 rounded-full">
                      <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-green-600">Applications</p>
                      <p className="text-2xl font-semibold text-green-900">{analytics.total_applications}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-purple-50 rounded-lg p-6">
                  <div className="flex items-center">
                    <div className="p-3 bg-purple-100 rounded-full">
                      <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-purple-600">Avg Match Score</p>
                      <p className="text-2xl font-semibold text-purple-900">
                        {analytics.match_score_stats?.average || 0}%
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-indigo-50 rounded-lg p-6">
                  <div className="flex items-center">
                    <div className="p-3 bg-indigo-100 rounded-full">
                      <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-indigo-600">Top Candidates</p>
                      <p className="text-2xl font-semibold text-indigo-900">
                        {analytics.match_score_stats?.above_70 || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Application Status Breakdown */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h4 className="text-lg font-medium text-gray-900 mb-4">Application Status</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(analytics.applications_by_status || {}).map(([status, count]) => (
                    <div key={status} className="text-center">
                      <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status)} mb-2`}>
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                      </div>
                      <p className="text-2xl font-semibold text-gray-900">{count}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Match Score Distribution */}
              {analytics.match_score_stats && Object.keys(analytics.match_score_stats).length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Match Score Distribution</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-600">Highest Score</p>
                      <p className="text-xl font-semibold text-green-600">{analytics.match_score_stats.highest}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600">Average Score</p>
                      <p className="text-xl font-semibold text-blue-600">{analytics.match_score_stats.average}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600">70%+ Matches</p>
                      <p className="text-xl font-semibold text-purple-600">{analytics.match_score_stats.above_70}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Top Skills Found */}
              {analytics.top_skills_found && analytics.top_skills_found.length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Most Common Skills in Applications</h4>
                  <div className="space-y-2">
                    {analytics.top_skills_found.slice(0, 8).map((skillData, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-700">{skillData.skill}</span>
                        <div className="flex items-center">
                          <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                            <div
                              className="bg-indigo-600 h-2 rounded-full"
                              style={{ width: `${(skillData.count / analytics.total_applications) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600">{skillData.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Experience Distribution */}
              {analytics.experience_distribution && Object.keys(analytics.experience_distribution).length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Experience Level Distribution</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-600">0-2 Years</p>
                      <p className="text-xl font-semibold text-gray-900">{analytics.experience_distribution['0-2_years'] || 0}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600">3-5 Years</p>
                      <p className="text-xl font-semibold text-gray-900">{analytics.experience_distribution['3-5_years'] || 0}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600">6-10 Years</p>
                      <p className="text-xl font-semibold text-gray-900">{analytics.experience_distribution['6-10_years'] || 0}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-600">10+ Years</p>
                      <p className="text-xl font-semibold text-gray-900">{analytics.experience_distribution['10+_years'] || 0}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Recent Application Timeline */}
              {analytics.application_timeline && analytics.application_timeline.length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Application Timeline (Last 30 Days)</h4>
                  <div className="space-y-2">
                    {analytics.application_timeline.slice(-7).map((dayData, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-700">{formatDate(dayData.date)}</span>
                        <div className="flex items-center">
                          <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                            <div
                              className="bg-green-500 h-2 rounded-full"
                              style={{ width: `${Math.min((dayData.count / Math.max(...analytics.application_timeline.map(d => d.count))) * 100, 100)}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-900">{dayData.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>

        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobAnalyticsModal;