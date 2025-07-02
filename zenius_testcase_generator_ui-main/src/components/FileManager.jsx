import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CONFIG from '../config';

const FileManager = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchUploadedFiles();
  }, []);

  const fetchUploadedFiles = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${CONFIG.API_BASE_URL}/api/list-uploaded-files`);
      setUploadedFiles(response.data);
    } catch (error) {
      console.error('Error fetching uploaded files:', error);
      setError('Failed to fetch uploaded files');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setError('');
    setSuccess('');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('fileType', selectedFile.type);

      const response = await axios.post(`${CONFIG.API_BASE_URL}/api/upload-and-view`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess(`File "${selectedFile.name}" uploaded successfully!`);
      setSelectedFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) {
        fileInput.value = '';
      }

      // Refresh the file list
      fetchUploadedFiles();
    } catch (error) {
      console.error('Error uploading file:', error);
      setError('Failed to upload file: ' + (error.response?.data || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleViewFile = async (fileName) => {
    try {
      const viewUrl = `${CONFIG.API_BASE_URL}/api/view-file/${fileName}`;
      
      // Open in new tab/window - Chrome will handle the file type appropriately
      const newWindow = window.open(viewUrl, '_blank', 'noopener,noreferrer');
      
      if (!newWindow) {
        setError('Please allow popups to view files');
      } else {
        setSuccess(`Opening ${fileName} in new tab`);
      }
    } catch (error) {
      console.error('Error viewing file:', error);
      setError('Failed to open file for viewing');
    }
  };

  const handleDeleteFile = async (fileName) => {
    if (!window.confirm(`Are you sure you want to delete "${fileName}"?`)) {
      return;
    }

    try {
      await axios.delete(`${CONFIG.API_BASE_URL}/api/delete-file/${fileName}`);
      setSuccess(`File "${fileName}" deleted successfully`);
      fetchUploadedFiles();
    } catch (error) {
      console.error('Error deleting file:', error);
      setError('Failed to delete file: ' + (error.response?.data || error.message));
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getFileIcon = (fileName) => {
    const extension = fileName.split('.').pop().toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'doc':
      case 'docx':
        return '📝';
      case 'xls':
      case 'xlsx':
        return '📊';
      case 'txt':
        return '📃';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return '🖼️';
      default:
        return '📁';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-orange-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-xl shadow-orange-lg p-8 border border-orange-100">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">File Manager</h2>
          
          {/* Error/Success Messages */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700">{error}</p>
            </div>
          )}
          
          {success && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-700">{success}</p>
            </div>
          )}

          {/* File Upload Section */}
          <div className="mb-8 p-6 bg-orange-50 border border-orange-200 rounded-lg">
            <h3 className="text-lg font-medium text-gray-800 mb-4">Upload New File</h3>
            <div className="flex items-center space-x-4">
              <input
                id="file-input"
                type="file"
                onChange={handleFileSelect}
                className="flex-1 p-3 border border-orange-200 rounded-lg cursor-pointer transition-all duration-200 hover:border-orange-300 bg-white text-gray-800 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-orange-100 file:text-orange-700 hover:file:bg-orange-200"
                accept=".pdf,.doc,.docx,.txt,.xls,.xlsx,.jpg,.jpeg,.png,.gif"
              />
              <button
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
                className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                  !selectedFile || uploading
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-orange-500 text-white hover:bg-orange-600 hover:shadow-lg'
                }`}
              >
                {uploading ? 'Uploading...' : 'Upload File'}
              </button>
            </div>
            {selectedFile && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
              </p>
            )}
          </div>

          {/* Uploaded Files List */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-800">Uploaded Files</h3>
              <button
                onClick={fetchUploadedFiles}
                disabled={loading}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200 disabled:opacity-50"
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>

            {loading ? (
              <div className="text-center py-8">
                <p className="mt-2 text-gray-600">Loading files...</p>
              </div>
            ) : uploadedFiles.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No files uploaded yet</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                    <div className="flex items-center space-x-4">
                      <span className="text-2xl">{getFileIcon(file.fileName)}</span>
                      <div>
                        <p className="font-medium text-gray-800">{file.fileName}</p>
                        <p className="text-sm text-gray-600">
                          {formatFileSize(file.size)} • {formatDate(file.lastModified)}
                        </p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleViewFile(file.fileName)}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200 font-medium"
                        title="View file in browser"
                      >
                        View
                      </button>
                      <button
                        onClick={() => handleDeleteFile(file.fileName)}
                        className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors duration-200 font-medium"
                        title="Delete file"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileManager; 