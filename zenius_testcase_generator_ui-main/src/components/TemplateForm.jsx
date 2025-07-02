import React, { useState } from "react";
import CONFIG from '../config'; 

const TemplateForm = ({ onBack }) => {
  const [projectName, setProjectName] = useState("");
  const [templateId, setTemplateId] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [errors, setErrors] = useState({ projectName: "", file: "" });

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const fileExtension = selectedFile.name.split(".").pop().toLowerCase();
      if (fileExtension !== "xlsx") {
        setErrors((prev) => ({ ...prev, file: "Only .xlsx files are allowed." }));
        setFile(null);
      } else {
        setErrors((prev) => ({ ...prev, file: "" })); 
        setFile(selectedFile);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    setErrors({ projectName: "", file: "" });

    let isValid = true;

    if (!file) {
      setErrors((prev) => ({ ...prev, file: "Please select a file." }));
      isValid = false;
    }

    if (!isValid) {
      setLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append("projectName", projectName);
    formData.append("templateId", templateId);
    formData.append("file", file);

    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.CREATE_TEMPLATE}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText);
      }

      setMessage({ type: "success", text: "Template uploaded successfully!" });
      setProjectName("");
      setTemplateId("");
      setFile(null);
    } catch (error) {
      console.error("Upload error:", error);
      
       if (error.message.includes("Template for project already exists")) {
        setErrors((prev) => ({ ...prev, projectName: "Project Name is already in use." }));
      } else if (error.message.includes("Template ID already exists")) {
        setErrors((prev) => ({ ...prev, templateId: "Template ID is already in use." }));
      }
      else {
        setMessage({ type: "error", text: error.message || "Upload failed." });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadSample = () => {
    window.open(`${CONFIG.API_BASE_URL}${CONFIG.DOWNLOAD_TEMPLATE}`, "_blank");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-orange-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header with back button */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Template Generator</h1>
            <p className="text-gray-600 mt-2">Upload and manage your test case templates</p>
          </div>
          <button
            onClick={onBack}
            className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors duration-200 font-medium shadow-orange"
          >
            ← Back to Home
          </button>
        </div>

        {/* Main content card */}
        <div className="bg-white rounded-xl shadow-orange-lg p-8 border border-orange-100">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-semibold text-gray-800">Upload Template</h2>
          </div>

          {/* Success/Error Messages */}
          {message?.type === "success" && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-700 font-medium">{message.text}</p>
            </div>
          )}

          {message?.type === "error" && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 font-medium">{message.text}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Project Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Name *
              </label>
              <input
                className="w-full p-3 border border-orange-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white text-gray-800 transition-all duration-200 hover:border-orange-300"
                type="text"
                placeholder="Enter project name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                required
              />
              {errors.projectName && (
                <p className="text-red-500 text-sm mt-1">{errors.projectName}</p>
              )}
            </div>

            {/* Template ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template ID *
              </label>
              <input
                className="w-full p-3 border border-orange-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white text-gray-800 transition-all duration-200 hover:border-orange-300"
                type="text"
                placeholder="Enter template ID"
                value={templateId}
                onChange={(e) => setTemplateId(e.target.value)}
                required
              />
              {errors.templateId && (
                <p className="text-red-500 text-sm mt-1">{errors.templateId}</p>
              )}
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template File * (.xlsx only)
              </label>
              <div className="relative">
                <input
                  type="file"
                  className="w-full p-3 border border-orange-200 rounded-lg cursor-pointer transition-all duration-200 hover:border-orange-300 bg-white text-gray-800 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                  onChange={handleFileChange}
                  accept=".xlsx"
                  required
                />
              </div>
              {errors.file && (
                <p className="text-red-500 text-sm mt-1">{errors.file}</p>
              )}
              {file && (
                <p className="text-green-600 text-sm mt-1">
                  ✓ Selected: {file.name}
                </p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-6">
              <button
                type="button"
                onClick={handleDownloadSample}
                className="flex-1 sm:flex-none px-6 py-3 bg-gray-500 text-white rounded-lg font-medium transition-all duration-200 hover:bg-gray-600 hover:shadow-md flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download Sample File
              </button>
              
              <button
                type="submit"
                className={`flex-1 px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
                  loading 
                    ? "bg-gray-400 cursor-not-allowed" 
                    : "bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 hover:shadow-orange-lg transform hover:scale-[1.02]"
                } text-white`}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Uploading...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    Upload Template
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Help Section */}
          <div className="mt-8 p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <h3 className="text-sm font-medium text-orange-800 mb-2">📋 Instructions</h3>
            <ul className="text-sm text-orange-700 space-y-1">
              <li>• Download the sample file to see the required format</li>
              <li>• Only .xlsx files are supported</li>
              <li>• Project names and template IDs must be unique</li>
              <li>• Make sure your template follows the required structure</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateForm; 