import React, { useState } from 'react';
import FileUpload from '../common/FileUpload';
import apiService from '../../services/api';

const JobApplicationModal = ({ job, onClose, onApplicationSubmitted }) => {
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [applicationResult, setApplicationResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileSelect = async (file, jobId) => {
    setLoading(true);
    setError('');
    setUploadStatus('Uploading and analyzing resume...');

    try {
      const formData = new FormData();
      formData.append('resume', file);
      formData.append('job_id', job.id);

      const response = await apiService.uploadResume(formData);
      
      setApplicationResult(response.resume);
      setUploadStatus('Application submitted successfully!');
      
      if (onApplicationSubmitted) {
        onApplicationSubmitted(response.resume);
      }

      // Auto close after 3 seconds
      setTimeout(() => {
        onClose();
      }, 3000);

    } catch (error) {
      console.error('Failed to submit application:', error);
      setError(error.message || 'Failed to submit application. Please try again.');
      setUploadStatus('');
    } finally {
      setLoading(false);
    }
  };

  const formatSkills = (skills) => {
    if (!skills || skills.length === 0) return 'None specified';
    return skills.slice(0, 5).join(', ') + (skills.length > 5 ? '...' : '');
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Apply for Position</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
              disabled={loading}
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="px-6 py-6">
          {/* Job Information */}
          <div className="mb-6">
            <h4 className="text-xl font-semibold text-gray-900 mb-2">{job.title}</h4>
            <p className="text-gray-600 mb-2">{job.company}</p>
            <div className="text-sm text-gray-500 space-y-1">
              <p>📍 {job.location}</p>
              <p>💼 {job.experience_required}</p>
              {job.salary_range && <p>💰 {job.salary_range}</p>}
            </div>
            <div className="mt-3">
              <p className="text-sm text-gray-700">
                <span className="font-medium">Required Skills:</span> {formatSkills(job.skills_required)}
              </p>
            </div>
          </div>

          {/* Application Status */}
          {uploadStatus && (
            <div className="mb-6">
              <div className={`p-4 rounded-md ${
                uploadStatus.includes('success') 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-blue-50 border border-blue-200'
              }`}>
                <div className="flex items-center">
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
                  ) : (
                    <svg className="w-5 h-5 text-green-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                  <p className="text-sm font-medium">{uploadStatus}</p>
                </div>
              </div>
            </div>
          )}

          {/* Application Results */}
          {applicationResult && (
            <div className="mb-6 bg-gray-50 p-4 rounded-md">
              <h5 className="font-medium text-gray-900 mb-3">Application Analysis</h5>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Match Score:</span>
                  <div className="flex items-center mt-1">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className={`h-2 rounded-full ${
                          applicationResult.match_score >= 70 ? 'bg-green-500' :
                          applicationResult.match_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(applicationResult.match_score, 100)}%` }}
                      ></div>
                    </div>
                    <span className="font-medium">{applicationResult.match_score}%</span>
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Status:</span>
                  <span className="ml-2 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                    {applicationResult.status}
                  </span>
                </div>
              </div>
              {applicationResult.parsed_skills && applicationResult.parsed_skills.length > 0 && (
                <div className="mt-3">
                  <span className="text-gray-600">Detected Skills:</span>
                  <p className="text-sm text-gray-800 mt-1">
                    {applicationResult.parsed_skills.slice(0, 8).join(', ')}
                    {applicationResult.parsed_skills.length > 8 && '...'}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    Application Failed
                  </h3>
                  <div className="mt-2 text-sm text-red-700">
                    {error}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* File Upload Section */}
          {!applicationResult && (
            <>
              <div className="mb-4">
                <h5 className="font-medium text-gray-900 mb-2">Upload Your Resume</h5>
                <p className="text-sm text-gray-600 mb-4">
                  Upload your resume and our AI will analyze how well it matches this position.
                </p>
              </div>

              <FileUpload
                onFileSelect={handleFileSelect}
                jobId={job.id}
                acceptedTypes=".pdf,.docx"
                maxSize={5 * 1024 * 1024} // 5MB
                className="mb-6"
              />

              {/* Tips */}
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <h6 className="font-medium text-blue-900 mb-2">💡 Tips for better matching:</h6>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Include relevant technical skills mentioned in the job description</li>
                  <li>• Highlight your experience that matches the required years</li>
                  <li>• Use clear section headers (Skills, Experience, Education)</li>
                  <li>• Save your resume as PDF for best results</li>
                </ul>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              disabled={loading}
            >
              {applicationResult ? 'Close' : 'Cancel'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobApplicationModal;