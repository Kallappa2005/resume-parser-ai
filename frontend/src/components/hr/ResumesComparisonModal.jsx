import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';

const ResumesComparisonModal = ({ resumeIds, onClose }) => {
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (resumeIds && resumeIds.length >= 2) {
      loadComparisonData();
    }
  }, [resumeIds]);

  const loadComparisonData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.compareResumes(resumeIds);
      setComparisonData(response);
    } catch (error) {
      console.error('Failed to load comparison data:', error);
      setError('Failed to load comparison data');
    } finally {
      setLoading(false);
    }
  };

  const getSkillMatchPercentage = (matchedCount, totalCount) => {
    if (totalCount === 0) return 0;
    return Math.round((matchedCount / totalCount) * 100);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getExperienceLevel = (years) => {
    if (years === 0) return 'Entry Level';
    if (years <= 2) return 'Junior';
    if (years <= 5) return 'Mid-Level';
    if (years <= 10) return 'Senior';
    return 'Expert';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-center mt-4">Loading comparison...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="text-center">
            <div className="text-red-600 text-lg mb-4">⚠️ Error</div>
            <p className="text-gray-700 mb-4">{error}</p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!comparisonData) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-7xl w-full h-[95vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xl font-bold text-gray-900">
                Candidate Comparison ({comparisonData.resumes.length} candidates)
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Side-by-side comparison of candidate profiles and match scores
              </p>
            </div>
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

        {/* Comparison Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            {/* Match Score Overview */}
            <div className="mb-8">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">📊 Match Score Overview</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {comparisonData.resumes.map((resume, index) => (
                  <div key={resume.id} className="bg-white border border-gray-200 rounded-lg p-4 text-center relative">
                    {index === 0 && (
                      <div className="absolute -top-2 -right-2 bg-yellow-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                        TOP PICK
                      </div>
                    )}
                    <h5 className="font-medium text-gray-900 truncate" title={resume.candidate_name}>
                      {resume.candidate_name}
                    </h5>
                    <div className={`text-3xl font-bold mt-2 mb-1 px-2 py-1 rounded ${getScoreColor(resume.match_score)}`}>
                      {Math.round(resume.match_score)}%
                    </div>
                    <p className="text-xs text-gray-500">Overall Match</p>
                    
                    {/* Match Breakdown Bars */}
                    <div className="mt-3 space-y-2">
                      <div className="flex justify-between items-center text-xs">
                        <span>Skills:</span>
                        <span>{Math.round(resume.match_breakdown.skills_score)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{width: `${resume.match_breakdown.skills_score}%`}}
                        ></div>
                      </div>
                      
                      <div className="flex justify-between items-center text-xs">
                        <span>Experience:</span>
                        <span>{Math.round(resume.match_breakdown.experience_score)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{width: `${resume.match_breakdown.experience_score}%`}}
                        ></div>
                      </div>
                      
                      <div className="flex justify-between items-center text-xs">
                        <span>Education:</span>
                        <span>{Math.round(resume.match_breakdown.education_score)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-600 h-2 rounded-full" 
                          style={{width: `${resume.match_breakdown.education_score}%`}}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Detailed Comparison Table */}
            <div className="mb-8">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">🔍 Detailed Comparison</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="sticky left-0 bg-gray-50 px-4 py-3 text-left text-sm font-medium text-gray-900 border-r">
                        Criteria
                      </th>
                      {comparisonData.resumes.map((resume) => (
                        <th key={resume.id} className="px-4 py-3 text-left text-sm font-medium text-gray-900 min-w-48">
                          <div>
                            <div className="font-semibold truncate" title={resume.candidate_name}>
                              {resume.candidate_name}
                            </div>
                            <div className="text-xs text-gray-500 truncate" title={resume.candidate_email}>
                              {resume.candidate_email}
                            </div>
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {/* Match Score Row */}
                    <tr className="hover:bg-gray-50">
                      <td className="sticky left-0 bg-white px-4 py-3 font-medium text-gray-900 border-r">
                        Overall Match Score
                      </td>
                      {comparisonData.resumes.map((resume, index) => (
                        <td key={resume.id} className="px-4 py-3 relative">
                          <span className={`px-2 py-1 rounded-full text-sm font-semibold ${getScoreColor(resume.match_score)}`}>
                            {Math.round(resume.match_score)}%
                          </span>
                          {index === 0 && (
                            <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                              🏆 WINNER
                            </span>
                          )}
                        </td>
                      ))}
                    </tr>

                    {/* Skills Score Breakdown */}
                    <tr className="hover:bg-gray-50">
                      <td className="sticky left-0 bg-white px-4 py-3 font-medium text-gray-900 border-r">
                        Skills Score (60% weight)
                      </td>
                      {comparisonData.resumes.map((resume, index) => (
                        <td key={resume.id} className="px-4 py-3">
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-sm font-semibold ${getScoreColor(resume.match_breakdown.skills_score)}`}>
                              {Math.round(resume.match_breakdown.skills_score)}%
                            </span>
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full" 
                                style={{width: `${resume.match_breakdown.skills_score}%`}}
                              ></div>
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {resume.match_breakdown.matched_skills.length} of {resume.skills.length} skills matched
                          </p>
                        </td>
                      ))}
                    </tr>

                    {/* Experience Score Breakdown */}
                    <tr className="hover:bg-gray-50">
                      <td className="sticky left-0 bg-white px-4 py-3 font-medium text-gray-900 border-r">
                        Experience Score (30% weight)
                      </td>
                      {comparisonData.resumes.map((resume) => (
                        <td key={resume.id} className="px-4 py-3">
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-sm font-semibold ${getScoreColor(resume.match_breakdown.experience_score)}`}>
                              {Math.round(resume.match_breakdown.experience_score)}%
                            </span>
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-green-600 h-2 rounded-full" 
                                style={{width: `${resume.match_breakdown.experience_score}%`}}
                              ></div>
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {resume.experience_years} years - {getExperienceLevel(resume.experience_years)}
                          </p>
                        </td>
                      ))}
                    </tr>

                    {/* Education Score Breakdown */}
                    <tr className="hover:bg-gray-50">
                      <td className="sticky left-0 bg-white px-4 py-3 font-medium text-gray-900 border-r">
                        Education Score (10% weight)
                      </td>
                      {comparisonData.resumes.map((resume) => (
                        <td key={resume.id} className="px-4 py-3">
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-sm font-semibold ${getScoreColor(resume.match_breakdown.education_score)}`}>
                              {Math.round(resume.match_breakdown.education_score)}%
                            </span>
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-purple-600 h-2 rounded-full" 
                                style={{width: `${resume.match_breakdown.education_score}%`}}
                              ></div>
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {resume.education_level}
                          </p>
                        </td>
                      ))}
                    </tr>

                    {/* Experience Row */}
                    <tr className="hover:bg-gray-50 bg-blue-25">
                      <td className="sticky left-0 bg-blue-25 px-4 py-3 font-medium text-gray-900 border-r">
                        📊 Detailed Experience Analysis
                      </td>
                      {comparisonData.resumes.map((resume, index) => (
                        <td key={resume.id} className="px-4 py-3">
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-lg">{resume.experience_years} years</span>
                              {index === 0 && comparisonData.resumes.length > 1 && resume.experience_years > comparisonData.resumes[1].experience_years && (
                                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                  +{resume.experience_years - comparisonData.resumes[1].experience_years} years more
                                </span>
                              )}
                            </div>
                            <div className="text-sm text-gray-600">
                              <span className={`px-2 py-1 rounded ${
                                resume.experience_years >= 5 ? 'bg-green-100 text-green-800' :
                                resume.experience_years >= 2 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {getExperienceLevel(resume.experience_years)}
                              </span>
                            </div>
                          </div>
                        </td>
                      ))}
                    </tr>

                    {/* Skills Match Row */}
                    <tr className="hover:bg-gray-50 bg-green-25">
                      <td className="sticky left-0 bg-green-25 px-4 py-3 font-medium text-gray-900 border-r">
                        🎯 Skills Compatibility Analysis
                      </td>
                      {comparisonData.resumes.map((resume, index) => (
                        <td key={resume.id} className="px-4 py-3">
                          <div className="space-y-3">
                            {/* Skills Match Stats */}
                            <div className="flex items-center justify-between">
                              <span className="font-medium">
                                {resume.match_breakdown.matched_skills.length}/{resume.skills.length} skills
                              </span>
                              <span className={`px-2 py-1 rounded text-xs font-medium ${getScoreColor(getSkillMatchPercentage(resume.match_breakdown.matched_skills.length, resume.skills.length))}`}>
                                {getSkillMatchPercentage(resume.match_breakdown.matched_skills.length, resume.skills.length)}% match
                              </span>
                            </div>
                            
                            {/* Advantage indicator */}
                            {index === 0 && comparisonData.resumes.length > 1 && resume.match_breakdown.matched_skills.length > comparisonData.resumes[1].match_breakdown.matched_skills.length && (
                              <div className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                                +{resume.match_breakdown.matched_skills.length - comparisonData.resumes[1].match_breakdown.matched_skills.length} more matched skills
                              </div>
                            )}
                            
                            {/* Matched Skills Preview */}
                            <div className="flex flex-wrap gap-1">
                              {resume.match_breakdown.matched_skills.slice(0, 3).map((skill, skillIndex) => (
                                <span key={skillIndex} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                  ✅ {skill}
                                </span>
                              ))}
                              {resume.match_breakdown.matched_skills.length > 3 && (
                                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                  +{resume.match_breakdown.matched_skills.length - 3} more
                                </span>
                              )}
                            </div>

                            {/* Missing Skills Preview */}
                            {resume.match_breakdown.missing_skills.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {resume.match_breakdown.missing_skills.slice(0, 2).map((skill, skillIndex) => (
                                  <span key={skillIndex} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                                    ❌ {skill}
                                  </span>
                                ))}
                                {resume.match_breakdown.missing_skills.length > 2 && (
                                  <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                    +{resume.match_breakdown.missing_skills.length - 2} missing
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </td>
                      ))}
                    </tr>

                    {/* Projects & Certifications Analysis */}
                    <tr className="hover:bg-gray-50 bg-purple-25">
                      <td className="sticky left-0 bg-purple-25 px-4 py-3 font-medium text-gray-900 border-r">
                        🚀 Projects & Certifications
                      </td>
                      {comparisonData.resumes.map((resume, index) => (
                        <td key={resume.id} className="px-4 py-3">
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium">Projects: {resume.projects.length}</span>
                              {index === 0 && comparisonData.resumes.length > 1 && resume.projects.length > comparisonData.resumes[1].projects.length && (
                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                  +{resume.projects.length - comparisonData.resumes[1].projects.length} more
                                </span>
                              )}
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium">Certifications: {resume.certifications.length}</span>
                              {index === 0 && comparisonData.resumes.length > 1 && resume.certifications.length > comparisonData.resumes[1].certifications.length && (
                                <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                                  +{resume.certifications.length - comparisonData.resumes[1].certifications.length} more
                                </span>
                              )}
                            </div>
                            
                            {/* Overall Portfolio Score */}
                            <div className="mt-2">
                              <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                                resume.projects.length + resume.certifications.length >= 3 ? 'bg-green-100 text-green-800' :
                                resume.projects.length + resume.certifications.length >= 1 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-gray-100 text-gray-600'
                              }`}>
                                {resume.projects.length + resume.certifications.length >= 3 ? 'Strong Portfolio' :
                                 resume.projects.length + resume.certifications.length >= 1 ? 'Moderate Portfolio' :
                                 'Limited Portfolio'}
                              </div>
                            </div>
                          </div>
                        </td>
                      ))}
                    </tr>

                    {/* Status Row */}
                    <tr className="hover:bg-gray-50">
                      <td className="sticky left-0 bg-white px-4 py-3 font-medium text-gray-900 border-r">
                        Application Status
                      </td>
                      {comparisonData.resumes.map((resume) => (
                        <td key={resume.id} className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            resume.status === 'shortlisted' ? 'bg-green-100 text-green-800' :
                            resume.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {resume.status.charAt(0).toUpperCase() + resume.status.slice(1)}
                          </span>
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Skills Breakdown */}
            <div className="mb-8">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">🛠️ Skills Breakdown</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {comparisonData.resumes.map((resume) => (
                  <div key={resume.id} className="bg-white border border-gray-200 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-3 truncate" title={resume.candidate_name}>
                      {resume.candidate_name}
                    </h5>
                    
                    {/* Matched Skills */}
                    {resume.match_breakdown.matched_skills.length > 0 && (
                      <div className="mb-3">
                        <h6 className="text-sm font-medium text-green-700 mb-2">
                          ✅ Matched Skills ({resume.match_breakdown.matched_skills.length})
                        </h6>
                        <div className="flex flex-wrap gap-1">
                          {resume.match_breakdown.matched_skills.slice(0, 8).map((skill, index) => (
                            <span key={index} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                              {skill}
                            </span>
                          ))}
                          {resume.match_breakdown.matched_skills.length > 8 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                              +{resume.match_breakdown.matched_skills.length - 8} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Missing Skills */}
                    {resume.match_breakdown.missing_skills.length > 0 && (
                      <div>
                        <h6 className="text-sm font-medium text-red-700 mb-2">
                          ❌ Missing Skills ({resume.match_breakdown.missing_skills.length})
                        </h6>
                        <div className="flex flex-wrap gap-1">
                          {resume.match_breakdown.missing_skills.slice(0, 6).map((skill, index) => (
                            <span key={index} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                              {skill}
                            </span>
                          ))}
                          {resume.match_breakdown.missing_skills.length > 6 && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                              +{resume.match_breakdown.missing_skills.length - 6} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Enhanced Recommendation */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
              <h4 className="text-xl font-bold text-blue-900 mb-4 flex items-center">
                🎯 AI-Powered Hiring Recommendation
              </h4>
              
              <div className="grid md:grid-cols-2 gap-6">
                {/* Winner Analysis */}
                <div className="bg-white rounded-lg p-4 border-l-4 border-yellow-400">
                  <h5 className="font-bold text-gray-900 mb-3 flex items-center">
                    🏆 Top Candidate: {comparisonData.resumes[0].candidate_name}
                    <span className="ml-2 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                      {Math.round(comparisonData.resumes[0].match_score)}% Match
                    </span>
                  </h5>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center text-green-700">
                      <span className="mr-2">✅</span>
                      <span><strong>Superior Skills Match:</strong> {comparisonData.resumes[0].match_breakdown.matched_skills.length} relevant skills identified</span>
                    </div>
                    
                    <div className="flex items-center text-green-700">
                      <span className="mr-2">✅</span>
                      <span><strong>Strong Experience:</strong> {comparisonData.resumes[0].experience_years} years ({getExperienceLevel(comparisonData.resumes[0].experience_years)})</span>
                    </div>
                    
                    {comparisonData.resumes[0].projects.length > 0 && (
                      <div className="flex items-center text-green-700">
                        <span className="mr-2">✅</span>
                        <span><strong>Proven Track Record:</strong> {comparisonData.resumes[0].projects.length} project{comparisonData.resumes[0].projects.length > 1 ? 's' : ''} completed</span>
                      </div>
                    )}
                    
                    {comparisonData.resumes[0].certifications.length > 0 && (
                      <div className="flex items-center text-green-700">
                        <span className="mr-2">✅</span>
                        <span><strong>Certified Professional:</strong> {comparisonData.resumes[0].certifications.length} certification{comparisonData.resumes[0].certifications.length > 1 ? 's' : ''}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Competitive Analysis */}
                {comparisonData.resumes.length > 1 && (
                  <div className="bg-white rounded-lg p-4 border-l-4 border-gray-400">
                    <h5 className="font-bold text-gray-900 mb-3">
                      📊 Why {comparisonData.resumes[0].candidate_name} Outperforms Others
                    </h5>
                    
                    <div className="space-y-2 text-sm">
                      {comparisonData.resumes[0].match_score - comparisonData.resumes[1].match_score > 10 && (
                        <div className="flex items-center text-blue-700">
                          <span className="mr-2">🎯</span>
                          <span><strong>Higher Match Score:</strong> +{Math.round(comparisonData.resumes[0].match_score - comparisonData.resumes[1].match_score)}% better fit</span>
                        </div>
                      )}
                      
                      {comparisonData.resumes[0].match_breakdown.matched_skills.length > comparisonData.resumes[1].match_breakdown.matched_skills.length && (
                        <div className="flex items-center text-blue-700">
                          <span className="mr-2">🛠️</span>
                          <span><strong>More Relevant Skills:</strong> +{comparisonData.resumes[0].match_breakdown.matched_skills.length - comparisonData.resumes[1].match_breakdown.matched_skills.length} additional matched skills</span>
                        </div>
                      )}
                      
                      {comparisonData.resumes[0].experience_years > comparisonData.resumes[1].experience_years && (
                        <div className="flex items-center text-blue-700">
                          <span className="mr-2">⏱️</span>
                          <span><strong>More Experience:</strong> +{comparisonData.resumes[0].experience_years - comparisonData.resumes[1].experience_years} years additional experience</span>
                        </div>
                      )}
                      
                      {comparisonData.resumes[0].projects.length > comparisonData.resumes[1].projects.length && (
                        <div className="flex items-center text-blue-700">
                          <span className="mr-2">🚀</span>
                          <span><strong>More Projects:</strong> +{comparisonData.resumes[0].projects.length - comparisonData.resumes[1].projects.length} additional projects</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Action Recommendations */}
              <div className="mt-6 p-4 bg-indigo-100 rounded-lg">
                <h6 className="font-bold text-indigo-900 mb-2">💡 Recommended Actions:</h6>
                <div className="text-sm text-indigo-800 space-y-1">
                  <div className="flex items-center">
                    <span className="mr-2">1.</span>
                    <span><strong>Priority Interview:</strong> Schedule {comparisonData.resumes[0].candidate_name} for the next available interview slot</span>
                  </div>
                  <div className="flex items-center">
                    <span className="mr-2">2.</span>
                    <span><strong>Skills Assessment:</strong> Focus on {comparisonData.resumes[0].match_breakdown.matched_skills.slice(0, 3).join(', ')} during technical evaluation</span>
                  </div>
                  {comparisonData.resumes[0].match_breakdown.missing_skills.length > 0 && (
                    <div className="flex items-center">
                      <span className="mr-2">3.</span>
                      <span><strong>Skill Gap Discussion:</strong> Address {comparisonData.resumes[0].match_breakdown.missing_skills.slice(0, 2).join(', ')} requirements during interview</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 flex-shrink-0">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              Close Comparison
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumesComparisonModal;