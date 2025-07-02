export const createTemplate = async (data) => {
    return await fetch("/api/create-template", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  };
  
  export const generateTestCases = async (data) => {
    return await fetch("/api/generate-test-cases", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  };
  