import { useState, useEffect, useRef } from "react";
import CreatableSelect from "react-select/creatable";
import axios from "axios";
import CONFIG from "../config";
import magic_icon from "../assests/magic icon.png";
// import { API_BASE_URL, PROJECTS_API, PROCESS_API, GENERATED_EXCEL, MODEL_OPTIONS, SOURCE_OPTIONS } from "../config";

const TestCaseForm = ({ onBack }) => {
  console.log("TestCaseForm rendered");
  const [projectName, setProjectName] = useState(null);
  const [modelName, setModelName] = useState(null);
  const [source, setSource] = useState(null);
  const [inputValue, setInputValue] = useState("");

  const [file, setFile] = useState(null);
  const [swadFile, setSwadFile] = useState(null);
  const [icdFile, setIcdFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [generatedFile, setGeneratedFile] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [projectOptions, setProjectOptions] = useState([]);
  const [errors, setErrors] = useState({});
  const fileInputRef = useRef(null);

  useEffect(() => {
    axios.get(`${CONFIG.API_BASE_URL}${CONFIG.PROJECTS_API}`)
      .then((response) => {
        console.log("Projects API response:", response.data);
        if (Array.isArray(response.data)) {
          const options = response.data.map((name) => ({
            value: name,
            label: name
          }));
          setProjectOptions(options);
        } else {
          console.error("Invalid data format for projects:", response.data);
        }
      })
      .catch((error) => console.error("Error fetching project names:", error));
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleViewFile = async (file) => {
    if (file) {
      try {
        // Upload the file first to get a viewable URL
        const formData = new FormData();
        formData.append('file', file);
        
        const uploadResponse = await axios.post(`${CONFIG.API_BASE_URL}/api/upload-and-view`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        if (uploadResponse.data.viewUrl) {
          // Open the file in a new tab using the server URL
          const viewUrl = `${CONFIG.API_BASE_URL}${uploadResponse.data.viewUrl}`;
          window.open(viewUrl, "_blank");
        }
      } catch (error) {
        console.error("Error uploading file for viewing:", error);
        // Fallback to local file viewing
        const fileUrl = URL.createObjectURL(file);
        window.open(fileUrl, "_blank");
      }
    }
  };

  const handleSourceChange = (selectedOption) => {
    setSource(selectedOption);
    setInputValue("");
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setGeneratedFile(null);

    let validationErrors = {};

    if (!projectName) validationErrors.projectName = "Project Name is required.";
    if (!modelName) validationErrors.modelName = "Model Name is required.";
    if (!source) validationErrors.source = "Source is required.";

    if ((source?.value === "jira" || source?.value === "confluence" || source?.value === "plaintext") && !inputValue.trim()) {
      validationErrors.inputValue = `Please enter a valid ${source.value === "plaintext" ? "Plain Text" : "URL"}.`;
    }

    if ((source?.value === "word" || source?.value === "text") && !file) {
      validationErrors.file = "Please upload a valid file.";
    }

    if (!swadFile) validationErrors.swadFile = "SWAD document is required.";
    if (!icdFile) validationErrors.icdFile = "ICD document is required.";

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setLoading(false);
      return;
    }

    setErrors({});

    try {
        let response;
        const formData = new FormData();
        formData.append("projectName", projectName?.value || projectName);
        formData.append("modelName", modelName?.value || modelName);
        formData.append("source", source?.value);
        formData.append("swadFile", swadFile);
        formData.append("icdFile", icdFile);
        if (source?.value === "plaintext")
        {
          formData.append("plainText",inputValue);
        }
        else if (source?.value === "word" || source?.value === "text") {
          formData.append("file", file);
        } else {
          formData.append(source?.value === "jira" || source?.value === "confluence" ? "link" : "plainText", inputValue);
        }

        response = await axios.post(`${CONFIG.API_BASE_URL}${CONFIG.PROCESS_API}${source?.value}`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        setGeneratedFile(response.data.excel_file);
        setDownloadUrl(response.data.download_url);
      }
     catch (error) {
      console.error("Error:", error);
      if (error.response && error.response.status === 400) {
        setErrors({ general: error.response.data });
      } else {
        console.log("here");
        setErrors({ general: "An unexpected error occurred. Please try again." });
      }
    }
    finally {
      setLoading(false);
    }
  };

  const customStyles = {
    control: (base) => ({
      ...base,
      padding: "8px",
      borderRadius: "8px",
      borderColor: "#fed7aa",
      boxShadow: "none",
      "&:hover": { borderColor: "#fb923c" },
      "&:focus-within": { 
        borderColor: "#f97316",
        boxShadow: "0 0 0 3px rgba(249, 115, 22, 0.1)"
      },
    }),
    option: (base, { isSelected, isFocused }) => ({
      ...base,
      backgroundColor: isSelected ? "#f97316" : isFocused ? "#fff7ed" : "#fff",
      color: isSelected ? "#fff" : "#374151",
      "&:hover": {
        backgroundColor: isSelected ? "#f97316" : "#fff7ed",
        color: isSelected ? "#fff" : "#374151",
      },
    }),
    singleValue: (base) => ({
      ...base,
      color: "#374151",
    }),
    placeholder: (base) => ({
      ...base,
      color: "#9ca3af",
    }),
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-orange-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header with back button */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Test Case Generator</h1>
            <p className="text-gray-600 mt-2">Generate comprehensive test cases automatically from your requirements</p>
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
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">Generate Test Cases</h2>

          {/* Error Messages */}
          {errors.general && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 font-medium">{errors.general}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Project Name *
                </label>
                <CreatableSelect
                  className="w-full"
                  placeholder="Select or Enter Project"
                  value={projectName}
                  onChange={setProjectName}
                  options={projectOptions}
                  isClearable
                  styles={customStyles}
                />
                {errors.projectName && (
                  <p className="text-red-500 text-sm mt-1">{errors.projectName}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model Name *
                </label>
                <CreatableSelect
                  className="w-full"
                  placeholder="Select or Enter Model"
                  value={modelName}
                  onChange={setModelName}
                  options={CONFIG.MODEL_OPTIONS}
                  isClearable
                  styles={customStyles}
                />
                {errors.modelName && (
                  <p className="text-red-500 text-sm mt-1">{errors.modelName}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Source Type *
                </label>
                <CreatableSelect
                  className="w-full"
                  placeholder="Select or Enter Source"
                  value={source}
                  onChange={handleSourceChange}
                  options={CONFIG.SOURCE_OPTIONS}
                  isClearable
                  styles={customStyles}
                />
                {errors.source && (
                  <p className="text-red-500 text-sm mt-1">{errors.source}</p>
                )}
              </div>
            </div>

            {/* Document Uploads */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload SWAD Document *
                </label>
                <div className="relative">
                  <div className="flex items-center space-x-2">
                    <input
                      type="file"
                      accept=".docx,.pdf"
                      onChange={(e) => setSwadFile(e.target.files[0])}
                      className="w-full p-3 border border-orange-200 rounded-lg cursor-pointer transition-all duration-200 hover:border-orange-300 bg-white text-gray-800 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                    />
                    {swadFile && (
                      <button
                        type="button"
                        onClick={() => handleViewFile(swadFile)}
                        className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                      >
                        View
                      </button>
                    )}
                  </div>
                 {swadFile && (
                   <p className="text-green-600 text-sm mt-1">✓ Selected: {swadFile.name}</p>
                 )}
                </div>
                {errors.swadFile && (
                  <p className="text-red-500 text-sm mt-1">{errors.swadFile}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload ICD Document *
                </label>
                <div className="relative">
                  <div className="flex items-center space-x-2">
                    <input
                      type="file"
                      accept=".docx,.pdf"
                      onChange={(e) => setIcdFile(e.target.files[0])}
                      className="w-full p-3 border border-orange-200 rounded-lg cursor-pointer transition-all duration-200 hover:border-orange-300 bg-white text-gray-800 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                    />
                    {icdFile && (
                      <button
                        type="button"
                        onClick={() => handleViewFile(icdFile)}
                        className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                      >
                        View
                      </button>
                    )}
                  </div>
                 {icdFile && (
                   <p className="text-green-600 text-sm mt-1">✓ Selected: {icdFile.name}</p>
                 )}
                </div>
                {errors.icdFile && (
                  <p className="text-red-500 text-sm mt-1">{errors.icdFile}</p>
                )}
              </div>
            </div>

            {/* Dynamic Input Based on Source */}
            {source && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {source?.value === "jira" || source?.value === "confluence" 
                    ? `${source.label} URL *`
                    : source?.value === "plaintext" 
                    ? "Plain Text Content *"
                    : source?.value === "word" || source?.value === "text"
                    ? "Upload File *"
                    : "Input *"
                  }
                </label>
                
                {source?.value === "jira" || source?.value === "confluence" ? (
                  <input
                    type="url"
                    className="w-full p-3 border border-orange-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white text-gray-800 transition-all duration-200 hover:border-orange-300"
                    placeholder={`Enter ${source.label} URL`}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                  />
                ) : source?.value === "plaintext" ? (
                  <textarea
                    className="w-full p-3 border border-orange-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white text-gray-800 transition-all duration-200 min-h-[120px] resize-y hover:border-orange-300"
                    placeholder="Enter your plain text content here..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                  />
                ) : source?.value === "word" || source?.value === "text" ? (
                  <div className="relative">
                    <div className="flex items-center space-x-2">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".docx,.txt"
                        className="w-full p-3 border border-orange-200 rounded-lg cursor-pointer transition-all duration-200 hover:border-orange-300 bg-white text-gray-800 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                        onChange={handleFileChange}
                      />
                      {file && (
                        <button
                          type="button"
                          onClick={() => handleViewFile(file)}
                          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                        >
                          View
                        </button>
                      )}
                    </div>
                    {file && (
                      <p className="text-green-600 text-sm mt-1">✓ Selected: {file.name}</p>
                    )}
                  </div>
                ) : null}
                
                {errors.inputValue && (
                  <p className="text-red-500 text-sm mt-1">{errors.inputValue}</p>
                )}
                {errors.file && (
                  <p className="text-red-500 text-sm mt-1">{errors.file}</p>
                )}
              </div>
            )}

            {/* Generate Button */}
            <div className="pt-6">
              <button
                type="submit"
                disabled={loading}
                className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-all duration-200 flex items-center justify-center gap-3 ${
                  loading
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 hover:shadow-orange-lg transform hover:scale-[1.02]"
                }`}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Generating Test Cases...</span>
                  </>
                ) : (
                  <>
                    <img src={magic_icon} alt="Magic Icon" className="h-6 w-6" />
                    <span>Generate Test Cases</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Generated File Result */}
          {generatedFile && downloadUrl && (
            <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-3 mb-3">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-lg font-semibold text-green-800">Test Cases Generated Successfully!</h3>
              </div>
              <p className="text-green-700 mb-4">Your test cases have been generated and are ready for download.</p>
              <a
                href={downloadUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 font-medium"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download {generatedFile}
              </a>
            </div>
          )}

          {/* Help Section */}
          <div className="mt-8 p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <h3 className="text-sm font-medium text-orange-800 mb-2">💡 Tips for Better Results</h3>
            <ul className="text-sm text-orange-700 space-y-1">
              <li>• Ensure your SWAD and ICD documents are properly formatted</li>
              <li>• For URLs, make sure they are accessible and contain relevant content</li>
              <li>• Plain text should be detailed and well-structured</li>
              <li>• Supported file formats: .docx, .pdf, .txt</li>
              <li>• The AI model will analyze your input to generate comprehensive test cases</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestCaseForm;
