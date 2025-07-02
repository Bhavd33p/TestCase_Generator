const CONFIG = {
    API_BASE_URL: "http://localhost:8081",
    PROJECTS_API: "/api/projects",
    PROCESS_API: "/api/process/",
    GENERATED_EXCEL: (generatedFile) => `${CONFIG.API_BASE_URL}/${generatedFile}`,
    DOWNLOAD_TEMPLATE: "/api/download-template",
    CREATE_TEMPLATE: "/api/create-template",
    MODEL_OPTIONS: [
      { value: "gpt-4o-mini", label: "GPT-4o Mini" },
      { value: "gpt-4o", label: "GPT-4o" },
    ],
    SOURCE_OPTIONS: [
      { value: "jira", label: "Jira" },
      { value: "confluence", label: "Confluence" },
      { value: "word", label: "Word Docx" },
      { value: "text", label: "Text Files" },
      { value: "plaintext", label: "Plain Text" },
    ],
  };
  
  export default CONFIG;
  