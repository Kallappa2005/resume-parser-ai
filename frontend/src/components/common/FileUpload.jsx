import React, { useState, useCallback } from 'react';

const FileUpload = ({ 
  onFileSelect, 
  acceptedTypes = '.pdf,.docx',
  maxSize = 5 * 1024 * 1024, // 5MB
  className = '',
  jobId = null
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const validateFile = (file) => {
    // Check file size
    if (file.size > maxSize) {
      return `File size must be less than ${maxSize / 1024 / 1024}MB`;
    }

    // Check file type
    const allowedTypes = acceptedTypes.split(',').map(type => type.trim());
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      return `Only ${allowedTypes.join(', ')} files are allowed`;
    }

    return null;
  };

  const handleFile = (file) => {
    const error = validateFile(file);
    if (error) {
      setUploadError(error);
      return;
    }

    setUploadError('');
    if (onFileSelect) {
      onFileSelect(file, jobId);
    }
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]); // Handle only first file
    }
  }, [onFileSelect, jobId]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  return (
    <div className={`${className}`}>
      <div
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200
          ${isDragOver 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${uploadError ? 'border-red-500 bg-red-50' : ''}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="space-y-4">
          {/* Upload Icon */}
          <div className="flex justify-center">
            <svg 
              className={`w-12 h-12 ${isDragOver ? 'text-blue-500' : 'text-gray-400'}`} 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
              />
            </svg>
          </div>

          {/* Upload Text */}
          <div>
            <p className="text-lg font-medium text-gray-900 mb-2">
              {isDragOver ? 'Drop your resume here' : 'Upload your resume'}
            </p>
            <p className="text-sm text-gray-600">
              Drag and drop your resume file here, or{' '}
              <label className="text-blue-600 hover:text-blue-500 cursor-pointer font-medium">
                browse to upload
                <input
                  type="file"
                  className="hidden"
                  accept={acceptedTypes}
                  onChange={handleFileInput}
                />
              </label>
            </p>
          </div>

          {/* File Requirements */}
          <div className="text-xs text-gray-500">
            <p>Supported formats: PDF, DOCX</p>
            <p>Maximum file size: {maxSize / 1024 / 1024}MB</p>
          </div>

          {/* Error Message */}
          {uploadError && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">
              {uploadError}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUpload;