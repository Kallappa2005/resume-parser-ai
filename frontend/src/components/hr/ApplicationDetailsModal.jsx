import React, { useState } from 'react';
import apiService from '../../services/api';

const ApplicationDetailsModal = ({ application, onClose, onStatusUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  const handleStatusUpdate = async (newStatus) => {
    setUpdating(true);
    try {
      console.log('Updating status:', application.id, newStatus);
      await apiService.updateResumeStatus(application.id, { status: newStatus });
      console.log('Status updated successfully');
      onStatusUpdate(application.id, newStatus);
      onClose();
    } catch (error) {
      console.error('Failed to update status:', error);
      alert(`Failed to update application status: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleDownload = async () => {
    setLoading(true);
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
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'shortlisted': return 'text-green-800 bg-green-100';
      case 'rejected': return 'text-red-800 bg-red-100';
      default: return 'text-yellow-800 bg-yellow-100';
    }
  };

  const parsedData = application.parsed_data || {};

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Application Details</h3>
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

        <div className="px-6 py-6 space-y-6">
          {/* Application Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4">Application Information</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Job Position</label>
                  <p className="text-sm text-gray-900">{application.job_title || 'N/A'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Applied Date</label>
                  <p className="text-sm text-gray-900">
                    {new Date(application.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(application.status)}`}>
                    {application.status.charAt(0).toUpperCase() + application.status.slice(1)}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Match Score</label>
                  <div className="flex items-center">
                    <span className="text-lg font-semibold text-blue-600">{application.match_score || 0}%</span>
                    <div className="ml-3 flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${application.match_score || 0}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4">Resume Actions</h4>
              <div className="space-y-3">
                <button
                  onClick={handleDownload}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Download Resume
                    </>
                  )}
                </button>
                <div className="text-sm text-gray-600">
                  <strong>Filename:</strong> {application.filename || 'N/A'}
                </div>
              </div>
            </div>
          </div>

          {/* Parsed Resume Data */}
          <div>
            <h4 className="text-lg font-medium text-gray-900 mb-4">Parsed Resume Analysis</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Skills */}
              <div>
                <h5 className="font-medium text-gray-700 mb-2">Skills Extracted</h5>
                {parsedData.skills && parsedData.skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {parsedData.skills.map((skill, index) => (
                      <span 
                        key={index}
                        className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No skills extracted</p>
                )}
              </div>

              {/* Experience */}
              <div>
                <h5 className="font-medium text-gray-700 mb-2">Experience</h5>
                <p className="text-sm text-gray-900">
                  {parsedData.total_experience_years || 0} years total experience
                </p>
                {parsedData.experience && parsedData.experience.length > 0 ? (
                  <div className="mt-2 space-y-2">
                    {parsedData.experience.slice(0, 3).map((exp, index) => (
                      <div key={index} className="text-sm text-gray-600">
                        • {typeof exp === 'string' ? exp : `${exp.position || 'Position'} at ${exp.company || 'Company'} (${exp.duration || 'N/A'})`}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No experience details extracted</p>
                )}
              </div>

              {/* Education */}
              <div>
                <h5 className="font-medium text-gray-700 mb-2">Education</h5>
                {parsedData.education && parsedData.education.length > 0 ? (
                  <div className="space-y-2">
                    {parsedData.education.map((edu, index) => (
                      <div key={index} className="text-sm text-gray-600">
                        • {typeof edu === 'string' ? edu : `${edu.degree || 'Degree'} from ${edu.institution || 'Institution'} (${edu.year || 'N/A'})`}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No education details extracted</p>
                )}
              </div>

              {/* Contact Info */}
              <div>
                <h5 className="font-medium text-gray-700 mb-2">Contact Information</h5>
                {parsedData.contact_info && Object.keys(parsedData.contact_info).length > 0 ? (
                  <div className="space-y-1 text-sm text-gray-600">
                    {Object.entries(parsedData.contact_info).map(([key, value]) => (
                      <div key={key}>
                        <strong>{key.charAt(0).toUpperCase() + key.slice(1)}:</strong> {typeof value === 'string' ? value : JSON.stringify(value)}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No contact information extracted</p>
                )}
              </div>
            </div>
          </div>

          {/* Status Management */}
          <div>
            <h4 className="text-lg font-medium text-gray-900 mb-4">Application Status Management</h4>
            <div className="flex space-x-3">
              <button
                onClick={() => handleStatusUpdate('shortlisted')}
                disabled={updating || application.status === 'shortlisted'}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center"
              >
                {updating ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                )}
                Shortlist
              </button>
              <button
                onClick={() => handleStatusUpdate('rejected')}
                disabled={updating || application.status === 'rejected'}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 disabled:opacity-50 flex items-center"
              >
                {updating ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
                Reject
              </button>
              <button
                onClick={() => handleStatusUpdate('pending')}
                disabled={updating || application.status === 'pending'}
                className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 disabled:opacity-50 flex items-center"
              >
                {updating ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
                Set Pending
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApplicationDetailsModal;