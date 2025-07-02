package com.zinnia.zenius.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.zinnia.zenius.service.*;
import com.zinnia.zenius.utils.ExcelGeneratorUtil;
import io.qameta.allure.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@SpringBootTest
@ExtendWith(MockitoExtension.class)
@Epic("Zenius AI Test Case Generator")
@Feature("Data Processing Controller")
class DataProcessingControllerTest {

    @Mock
    private WordTxtFilesProcessingService wordTxtFilesProcessingService;

    @Mock
    private JiraConfluenceLinkProcessingService jiraConfluenceLinkProcessingService;

    @Mock
    private ExcelGeneratorUtil excelGeneratorUtil;

    @Mock
    private TemplateService templateService;

    @Mock
    private GeneratedTestCaseService generatedTestCaseService;

    @Mock
    private RestTemplate restTemplate;

    @InjectMocks
    private DataProcessingController dataProcessingController;

    private static final String TEST_UPLOAD_DIR = "test-uploads";
    private static final String TEST_FILE_NAME = "test-document.pdf";
    private static final String TEST_FILE_CONTENT = "This is a test file content";

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(dataProcessingController, "fileUploadDirectory", TEST_UPLOAD_DIR);
        ReflectionTestUtils.setField(dataProcessingController, "excelOutputFolder", "test-output");
        ReflectionTestUtils.setField(dataProcessingController, "fileDownloadPrefixUrl", "http://localhost:8081/api/download-excel/");
        
        // Create test upload directory
        File uploadDir = new File(TEST_UPLOAD_DIR);
        if (!uploadDir.exists()) {
            uploadDir.mkdirs();
        }
    }

    @Test
    @DisplayName("Upload and View File - Success")
    @Description("Test successful file upload and generation of view URL")
    @Severity(SeverityLevel.CRITICAL)
    @Tag("file-upload")
    @Story("File Upload and Viewing")
    void testUploadAndViewFile_Success() {
        MockMultipartFile mockFile = new MockMultipartFile(
                "file",
                TEST_FILE_NAME,
                "application/pdf",
                TEST_FILE_CONTENT.getBytes()
        );

        Allure.step("Execute file upload", () -> {
            ResponseEntity<?> response = dataProcessingController.uploadAndViewFile(mockFile, "pdf");
            
            Allure.step("Verify response status", () -> {
                assertEquals(HttpStatus.OK, response.getStatusCode());
            });
            
            Allure.step("Verify response content", () -> {
                assertNotNull(response.getBody());
                @SuppressWarnings("unchecked")
                Map<String, Object> responseBody = (Map<String, Object>) response.getBody();
                assertEquals("File uploaded successfully", responseBody.get("message"));
                assertNotNull(responseBody.get("fileName"));
                assertEquals(TEST_FILE_NAME, responseBody.get("originalFileName"));
                assertNotNull(responseBody.get("viewUrl"));
                assertEquals((long) TEST_FILE_CONTENT.getBytes().length, responseBody.get("fileSize"));
            });
        });
    }

    @Test
    @DisplayName("Upload File - Null File")
    @Description("Test file upload with null file parameter")
    @Severity(SeverityLevel.NORMAL)
    @Tag("file-upload")
    @Tag("error-handling")
    @Story("File Upload Error Handling")
    void testUploadAndViewFile_NullFile() {
        Allure.step("Execute upload with null file", () -> {
            assertThrows(Exception.class, () -> {
                dataProcessingController.uploadAndViewFile(null, "pdf");
            });
        });
    }

    @Test
    @DisplayName("View File - Success")
    @Description("Test successful file viewing with proper content type")
    @Severity(SeverityLevel.CRITICAL)
    @Tag("file-viewing")
    @Story("File Viewing")
    void testViewFile_Success() throws IOException {
        Allure.step("Create test file", () -> {
            try {
                // Create a test file in the upload directory
                Path testFilePath = Paths.get(TEST_UPLOAD_DIR, TEST_FILE_NAME);
                Files.createDirectories(testFilePath.getParent());
                Files.write(testFilePath, TEST_FILE_CONTENT.getBytes());
            } catch (IOException e) {
                fail("Failed to create test file: " + e.getMessage());
            }
        });

        Allure.step("Execute file view request", () -> {
            ResponseEntity<Resource> response = dataProcessingController.viewFile(TEST_FILE_NAME);
            
            Allure.step("Verify response status", () -> {
                assertEquals(HttpStatus.OK, response.getStatusCode());
            });
            
            Allure.step("Verify response headers", () -> {
                assertNotNull(response.getHeaders().getContentType());
                assertTrue(response.getHeaders().getFirst("Content-Disposition").contains("inline"));
                assertEquals("no-cache, no-store, must-revalidate", 
                           response.getHeaders().getFirst("Cache-Control"));
            });
            
            Allure.step("Verify resource exists", () -> {
                assertNotNull(response.getBody());
                assertTrue(response.getBody().exists());
            });
        });
    }

    @Test
    @DisplayName("View File - File Not Found")
    @Description("Test file viewing when file does not exist")
    @Severity(SeverityLevel.NORMAL)
    @Tag("file-viewing")
    @Tag("error-handling")
    @Story("File Viewing Error Handling")
    void testViewFile_NotFound() {
        Allure.step("Execute view request for non-existent file", () -> {
            ResponseEntity<Resource> response = dataProcessingController.viewFile("non-existent-file.pdf");
            
            Allure.step("Verify 404 response", () -> {
                assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
                assertNull(response.getBody());
            });
        });
    }

    @Test
    @DisplayName("List Uploaded Files - Success")
    @Description("Test listing of uploaded files in directory")
    @Severity(SeverityLevel.NORMAL)
    @Tag("file-management")
    @Story("File Management")
    void testListUploadedFiles_Success() throws IOException {
        Allure.step("Create test files", () -> {
            try {
                // Create multiple test files
                Path testFile1 = Paths.get(TEST_UPLOAD_DIR, "test1.pdf");
                Path testFile2 = Paths.get(TEST_UPLOAD_DIR, "test2.docx");
                
                Files.createDirectories(testFile1.getParent());
                Files.write(testFile1, "Test content 1".getBytes());
                Files.write(testFile2, "Test content 2".getBytes());
            } catch (IOException e) {
                fail("Failed to create test files: " + e.getMessage());
            }
        });

        Allure.step("Execute list files request", () -> {
            ResponseEntity<List<Map<String, Object>>> response = dataProcessingController.listUploadedFiles();
            
            Allure.step("Verify response status", () -> {
                assertEquals(HttpStatus.OK, response.getStatusCode());
            });
            
            Allure.step("Verify file list content", () -> {
                assertNotNull(response.getBody());
                List<Map<String, Object>> fileList = response.getBody();
                assertTrue(fileList.size() >= 2);
                
                // Verify file information structure
                Map<String, Object> firstFile = fileList.get(0);
                assertNotNull(firstFile.get("fileName"));
                assertNotNull(firstFile.get("size"));
                assertNotNull(firstFile.get("lastModified"));
                assertNotNull(firstFile.get("viewUrl"));
            });
        });
    }

    @Test
    @DisplayName("List Uploaded Files - Empty Directory")
    @Description("Test listing files when upload directory is empty")
    @Severity(SeverityLevel.NORMAL)
    @Tag("file-management")
    @Story("File Management")
    void testListUploadedFiles_EmptyDirectory() {
        // Set a non-existent directory
        ReflectionTestUtils.setField(dataProcessingController, "fileUploadDirectory", "non-existent-dir");
        
        Allure.step("Execute list files request on empty directory", () -> {
            ResponseEntity<List<Map<String, Object>>> response = dataProcessingController.listUploadedFiles();
            
            Allure.step("Verify empty response", () -> {
                assertEquals(HttpStatus.OK, response.getStatusCode());
                assertNotNull(response.getBody());
                assertTrue(response.getBody().isEmpty());
            });
        });
    }

    @Test
    @DisplayName("Delete File - Success")
    @Description("Test successful file deletion")
    @Severity(SeverityLevel.NORMAL)
    @Tag("file-management")
    @Story("File Management")
    void testDeleteUploadedFile_Success() throws IOException {
        Allure.step("Create test file for deletion", () -> {
            try {
                Path testFilePath = Paths.get(TEST_UPLOAD_DIR, "file-to-delete.pdf");
                Files.createDirectories(testFilePath.getParent());
                Files.write(testFilePath, "Content to delete".getBytes());
            } catch (IOException e) {
                fail("Failed to create test file: " + e.getMessage());
            }
        });

        Allure.step("Execute file deletion", () -> {
            ResponseEntity<?> response = dataProcessingController.deleteUploadedFile("file-to-delete.pdf");
            
            Allure.step("Verify deletion response", () -> {
                assertEquals(HttpStatus.OK, response.getStatusCode());
                assertNotNull(response.getBody());
                Map<String, Object> responseBody = (Map<String, Object>) response.getBody();
                assertEquals("File deleted successfully", responseBody.get("message"));
                assertEquals("file-to-delete.pdf", responseBody.get("fileName"));
            });
            
            Allure.step("Verify file is actually deleted", () -> {
                Path deletedFilePath = Paths.get(TEST_UPLOAD_DIR, "file-to-delete.pdf");
                assertFalse(Files.exists(deletedFilePath));
            });
        });
    }

    @Test
    @DisplayName("Delete File - File Not Found")
    @Description("Test file deletion when file does not exist")
    @Severity(SeverityLevel.NORMAL)
    @Tag("file-management")
    @Tag("error-handling")
    @Story("File Management Error Handling")
    void testDeleteUploadedFile_NotFound() {
        Allure.step("Execute deletion of non-existent file", () -> {
            ResponseEntity<?> response = dataProcessingController.deleteUploadedFile("non-existent-file.pdf");
            
            Allure.step("Verify 404 response", () -> {
                assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
                assertNotNull(response.getBody());
                assertTrue(response.getBody().toString().contains("File not found"));
            });
        });
    }

    @Test
    @DisplayName("Get All Project Names - Success")
    @Description("Test successful retrieval of project names")
    @Severity(SeverityLevel.CRITICAL)
    @Tag("project-management")
    @Story("Project Management")
    void testGetAllProjectNames_Success() {
        List<String> mockProjectNames = List.of("Project1", "Project2", "Project3");
        when(templateService.getAllProjectNames()).thenReturn(mockProjectNames);

        Allure.step("Execute get project names request", () -> {
            ResponseEntity<List<String>> response = dataProcessingController.getAllProjectNames();
            
            Allure.step("Verify response", () -> {
                assertEquals(HttpStatus.OK, response.getStatusCode());
                assertNotNull(response.getBody());
                assertEquals(3, response.getBody().size());
                assertTrue(response.getBody().contains("Project1"));
                assertTrue(response.getBody().contains("Project2"));
                assertTrue(response.getBody().contains("Project3"));
            });
        });
    }

    @Test
    @DisplayName("Get All Project Names - Service Exception")
    @Description("Test project names retrieval when service throws exception")
    @Severity(SeverityLevel.NORMAL)
    @Tag("project-management")
    @Tag("error-handling")
    @Story("Project Management Error Handling")
    void testGetAllProjectNames_ServiceException() {
        when(templateService.getAllProjectNames()).thenThrow(new RuntimeException("Database connection failed"));

        Allure.step("Execute get project names with service exception", () -> {
            ResponseEntity<List<String>> response = dataProcessingController.getAllProjectNames();
            
            Allure.step("Verify error response", () -> {
                assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode());
                assertNotNull(response.getBody());
                assertTrue(response.getBody().isEmpty());
            });
        });
    }

    // Cleanup method to remove test files after tests
    void cleanupTestFiles() {
        try {
            Path uploadDir = Paths.get(TEST_UPLOAD_DIR);
            if (Files.exists(uploadDir)) {
                Files.walk(uploadDir)
                     .sorted((a, b) -> b.compareTo(a)) // Delete files before directories
                     .forEach(path -> {
                         try {
                             Files.delete(path);
                         } catch (IOException e) {
                             // Ignore cleanup errors
                         }
                     });
            }
        } catch (IOException e) {
            // Ignore cleanup errors
        }
    }
} 