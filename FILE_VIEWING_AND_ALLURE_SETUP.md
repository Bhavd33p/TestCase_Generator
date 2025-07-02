# File Viewing and Allure Reporting Setup Guide

This document provides instructions for using the new file viewing functionality and Allure reporting features added to the Zenius AI Test Case Generator.

## 🚀 New Features

### 1. File Viewing in Chrome
- **Upload files** through the UI and view them directly in Chrome browser
- **Supported file types**: PDF, Word documents, Excel files, text files, images
- **Secure file storage** on the server with proper access controls
- **File management** with upload, view, and delete capabilities

### 2. Enhanced Allure Reporting
- **Comprehensive test reporting** with detailed steps and screenshots
- **Test categorization** by feature, story, and severity
- **Rich annotations** with descriptions, tags, and links
- **Interactive HTML reports** with filtering and search capabilities

## 📁 File Viewing Setup

### Backend API Endpoints

The following new endpoints have been added to the DataProcessingController:

#### 1. Upload and View File
```http
POST /api/upload-and-view
Content-Type: multipart/form-data

Parameters:
- file: MultipartFile (required)
- fileType: String (optional)
```

#### 2. View File
```http
GET /api/view-file/{fileName}
```

#### 3. List Uploaded Files
```http
GET /api/list-uploaded-files
```

#### 4. Delete File
```http
DELETE /api/delete-file/{fileName}
```

### Configuration

Add these properties to your `application.properties`:
```properties
# File Upload Configuration
file.upload.directory=uploads
file.view.base.url=http://localhost:8081

# Multipart Configuration
spring.servlet.multipart.enabled=true
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=10MB
```

## 📊 Allure Reporting Setup

### Prerequisites
1. Install Allure CLI:
   ```bash
   # On Windows (using Chocolatey)
   choco install allure
   
   # On macOS (using Homebrew)
   brew install allure
   
   # On Linux (using npm)
   npm install -g allure-commandline
   ```

### Running Tests with Allure

#### 1. Run Tests and Generate Results
```bash
cd zenius-ai-testcase-generator-api-main
./gradlew test
```

#### 2. Generate and View Allure Report
```bash
# Generate report
./gradlew allureReport

# Serve report (opens in browser)
./gradlew serveAllureReport
```

### Usage Examples

#### File Viewing Example
```javascript
// Frontend - Upload and view file
const handleUploadAndView = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post('/api/upload-and-view', formData);
  
  // Open file in Chrome
  const viewUrl = `${API_BASE_URL}${response.data.viewUrl}`;
  window.open(viewUrl, '_blank');
};
```

#### Test Writing Example
```java
@Test
@DisplayName("File Upload - Success")
@Description("Test uploading a file and verify it can be viewed")
@Severity(SeverityLevel.CRITICAL)
@Tag("file-upload")
@Story("File Upload and Viewing")
void testFileUpload() {
    Allure.step("Upload file", () -> {
        // Upload file and verify response
    });
    
    Allure.step("Verify file can be viewed", () -> {
        // Test file viewing functionality
    });
}
```

## 🔧 How to Use

### 1. File Management
- Navigate to `/file-manager` in your application
- Upload files using the file input
- Click "View" to open files in Chrome
- Manage files with the provided controls

### 2. Enhanced Form File Viewing
- In TestCaseForm, uploaded files now have "View" buttons
- Files are uploaded to server for secure viewing
- Files open in new Chrome tabs with proper MIME types

### 3. Running Tests with Allure
```bash
# Run all tests with Allure reporting
./gradlew testWithAllure

# Clean previous results
./gradlew cleanAllure

# Serve report in browser
./gradlew serveAllureReport
```

## 🚨 Troubleshooting

### File Viewing Issues
1. **Files not opening**: Check popup blocker settings
2. **Upload failures**: Verify file size limits and directory permissions
3. **Access denied**: Ensure proper server configuration

### Allure Reporting Issues
1. **CLI not found**: Install Allure CLI and add to PATH
2. **Reports not generating**: Verify test results exist
3. **Browser not opening**: Try different browser or use direct command

## 📝 Best Practices

1. **Security**: Always validate file types and sizes
2. **Testing**: Use descriptive test names and proper categorization
3. **Reporting**: Clean old results regularly and share reports with team
4. **Error Handling**: Provide clear error messages for all operations

## 🔗 Additional Resources

- [Allure Framework Documentation](https://docs.qameta.io/allure/)
- [Spring Boot File Upload Guide](https://spring.io/guides/gs/uploading-files/)
- [Chrome File Viewing Best Practices](https://developers.google.com/web/fundamentals/security/csp)
- [JUnit 5 Testing Guide](https://junit.org/junit5/docs/current/user-guide/)

## 🤝 Contributing

When adding new features:
1. Include comprehensive tests with Allure annotations
2. Update this documentation
3. Add file viewing support where applicable
4. Follow existing code patterns and conventions 