package com.zinnia.zenius.controller;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.zinnia.zenius.model.GeneratedTestCase;
import com.zinnia.zenius.model.TestTemplate;
import com.zinnia.zenius.service.*;
import com.zinnia.zenius.utils.DataProcessingUtil;
import com.zinnia.zenius.utils.ExcelGeneratorUtil;
import com.zinnia.zenius.utils.PdfGeneratorUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.*;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;


@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "${frontend.url}")
public class DataProcessingController {
    private static final Logger logger = LoggerFactory.getLogger(DataProcessingController.class);
    private final WordTxtFilesProcessingService wordTxtFilesProcessingService;
    private final JiraConfluenceLinkProcessingService jiraConfluenceLinkProcessingService;
    private final ExcelGeneratorUtil excelGeneratorUtil;
    private final TemplateService templateService;
    private final GeneratedTestCaseService generatedTestCaseService;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${fastapi.testcases.url}")
    private String fastApiTestCasesBaseUrl;

    @Value("${fastapi.endpoint.generate-test-cases}")
    private String fastApiGenerateEndpoint;

    @Value("${excel.output.folder}")
    private String excelOutputFolder;

    @Value("${fastapi.token.limit}")
    private int tokenLimit;

    @Value("${file.download.prefix.url}")
    private String fileDownloadPrefixUrl;

    @Value("${file.upload.directory:uploads}")
    private String fileUploadDirectory;

    @Autowired
    public DataProcessingController(WordTxtFilesProcessingService wordTxtFilesProcessingService,
                                    JiraConfluenceLinkProcessingService jiraConfluenceLinkProcessingService,
                                    ExcelGeneratorUtil excelGeneratorUtil,
                                    TemplateService templateService,
                                    GeneratedTestCaseService generatedTestCaseService,
                                    RestTemplate restTemplate) {
        this.wordTxtFilesProcessingService = wordTxtFilesProcessingService;
        this.jiraConfluenceLinkProcessingService = jiraConfluenceLinkProcessingService;
        this.excelGeneratorUtil = excelGeneratorUtil;
        this.templateService = templateService;
        this.generatedTestCaseService = generatedTestCaseService;
        this.restTemplate = restTemplate;
    }

    @GetMapping("/projects")
    public ResponseEntity<List<String>> getAllProjectNames() {
        try {
            List<String> projectNames = templateService.getAllProjectNames();
            return ResponseEntity.ok(projectNames);
        } catch (Exception e) {
            logger.error("Error fetching project names", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Collections.emptyList());
        }
    }

    @PostMapping("/process/{source}")
    public ResponseEntity<?> processFileOrLink(
            @PathVariable("source") String source,
            @RequestParam(value = "file", required = false) MultipartFile file,
            @RequestParam(value = "link", required = false) String link,
            @RequestParam(value = "modelName") String modelName,
            @RequestParam(value = "projectName") String projectName,
            @RequestParam(value = "plainText", required = false) String plainText) {
        ResponseEntity<String> responseEntity = null;
        try {
            String extractedText = "";
            String uniqueIdentifier = null;

            Optional<TestTemplate> templateOptional = templateService.findTemplateOrDefault(projectName);

            if (templateOptional.isEmpty()) {
                logger.warn("No template found for project: {} or default template.", projectName);
                return ResponseEntity.badRequest().body("No template available for processing.");
            }

            if (plainText != null) {
                plainText = URLDecoder.decode(plainText, StandardCharsets.UTF_8);
            }

            TestTemplate template = templateOptional.get();
            List<String> templateColumns = template.getColumns();
            logger.info("Received Request from UI:");
            logger.info("Source: {}", source);
            logger.info("Project Name: {}", projectName);
            logger.info("Model Name: {}", modelName);

            if (plainText != null && !plainText.isBlank()) {
                logger.info("Plain Text Input:\n{}", plainText);
            } else {
                logger.info("No plain text input received.");
            }

            switch (source.toLowerCase()) {
                case "jira", "confluence" -> {
                    if (link == null || link.isBlank()) {
                        return ResponseEntity.badRequest().body("Please provide a valid Jira or Confluence link.");
                    }
                    Map<String, Object> data = jiraConfluenceLinkProcessingService.fetchData(link);
                    String description = (String) data.getOrDefault("description", "");
                    List<Map<String, String>> attachmentsData = (List<Map<String, String>>) data.getOrDefault("attachmentsData", Collections.emptyList());
                    StringBuilder combinedText = new StringBuilder(description);
                    for (Map<String, String> attachment : attachmentsData) {
                        combinedText.append("\n").append(attachment.get("content"));
                    }
                    extractedText = combinedText.toString();

                    uniqueIdentifier = DataProcessingUtil.extractIdFromLink(source, link);
                }
                case "word", "text" -> {
                    if (file == null || file.isEmpty()) {
                        return ResponseEntity.badRequest().body("Please upload a valid Word or Text file.");
                    }
                    extractedText = wordTxtFilesProcessingService.processFile(file);
                    try {
                        uniqueIdentifier = DataProcessingUtil.generateHash(extractedText);
                        logger.info("Generated Hash for {} file: {}", source, uniqueIdentifier);
                    } catch (NoSuchAlgorithmException e) {
                        logger.error("Error generating hash: {}", e.getMessage(), e);
                        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error generating hash: " + e.getMessage());
                    }
                }
                case "plaintext" -> {
                    if (plainText == null || plainText.isBlank()) {
                        return ResponseEntity.badRequest().body("Plain text input cannot be empty.");
                    }
                    extractedText = plainText.trim();
                    try {
                        uniqueIdentifier = DataProcessingUtil.generateHash(extractedText);
                        logger.info("Generated Hash for Plain Text: {}", uniqueIdentifier);
                    } catch (NoSuchAlgorithmException e) {
                        logger.error("Error generating hash: {}", e.getMessage(), e);
                        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error generating hash: " + e.getMessage());
                    }
                }
                default -> {
                    return ResponseEntity.badRequest().body("Invalid source type.");
                }
            }

            Optional<GeneratedTestCase> existingTestCase = generatedTestCaseService.findBySourceAndIdentifier(source, uniqueIdentifier);
            if (existingTestCase.isPresent()) {
                logger.info("Test cases already exist for source: {} and identifier: {}", source, uniqueIdentifier);
                List<Map<String, Object>> testCases = existingTestCase.get().getTestCases();
                String excelFilePath = excelGeneratorUtil.generateExcel(testCases, excelOutputFolder);
                logger.info("Excel file generated from MongoDB: {}", excelFilePath);

                return ResponseEntity.ok(Map.of(
                        "message", "Test cases fetched from database.",
                        "excel_file", excelFilePath.substring(excelFilePath.lastIndexOf("/") + 1),
                        "download_url", fileDownloadPrefixUrl + excelFilePath.substring(excelFilePath.lastIndexOf("/") + 1)
                ));
            }


            File pdfFile = PdfGeneratorUtil.createPdfFromText(extractedText, excelOutputFolder, "temp_input.pdf");
            int pageCount = PdfGeneratorUtil.getPageCount(pdfFile);
            logger.info("Generated PDF has {} pages", pageCount);

            MultiValueMap<String, Object> multipartRequest = new LinkedMultiValueMap<>();
            multipartRequest.add("file", new FileSystemResource(pdfFile));
            multipartRequest.add("project_name", projectName);
            multipartRequest.add("source", source);
            multipartRequest.add("model_name", modelName);
            multipartRequest.add("source_id", source.matches("jira|confluence") ? uniqueIdentifier : null);
            multipartRequest.add("template_columns", objectMapper.writeValueAsString(templateColumns));

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(multipartRequest, headers);
            responseEntity = restTemplate.postForEntity(fastApiTestCasesBaseUrl + fastApiGenerateEndpoint + source, requestEntity, String.class);
            String responseBody = responseEntity.getBody();
            logger.info("FastAPI Raw Response: {}", responseBody);

            if (!responseEntity.getStatusCode().is2xxSuccessful()) {
                logger.error("FastAPI returned error status: {}", responseEntity.getStatusCode());
                return ResponseEntity.status(responseEntity.getStatusCode())
                        .body("Error from FastAPI: " + responseBody);
            }

            // Parse and verify the response contains required fields
            try {
                JsonNode rootNode = objectMapper.readTree(responseBody);
                String message = rootNode.path("message").asText("");
                int testCasesCount = rootNode.path("test_cases_count").asInt(-1);
                String excelFile = rootNode.path("excel_file").asText("");
                String downloadUrl = rootNode.path("download_url").asText("");
                logger.info("FastAPI response: message={}, test_cases_count={}, excel_file={}, download_url={}", message, testCasesCount, excelFile, downloadUrl);
                if (downloadUrl.isEmpty() || excelFile.isEmpty()) {
                    logger.error("FastAPI response missing download_url or excel_file");
                    return ResponseEntity.badRequest().body("FastAPI response missing download_url or excel_file");
                }
                // Return the response as-is to the client
                return ResponseEntity.ok(rootNode);
            } catch (Exception e) {
                logger.error("Failed to parse FastAPI response: {}", e.getMessage(), e);
                return ResponseEntity.badRequest().body("Invalid response format from FastAPI: " + e.getMessage());
            }
        } catch (RestClientException e) {
            logger.error("Error communicating with FastAPI: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.GATEWAY_TIMEOUT).body("Error communicating with FastAPI: " + e.getMessage());
        } catch (IOException e) {
            logger.error("Error processing request: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error processing request: " + e.getMessage());
        } finally {
            if (responseEntity != null && responseEntity.getBody() != null) {
                try {
                    logger.info("Closing HTTP connection for FastAPI request.");
                    responseEntity = null;
                } catch (Exception e) {
                    logger.error("Error while closing connection: {}", e.getMessage(), e);
                }
            }
        }
    }
    @PostMapping("/process-json")
    public ResponseEntity<?> processJsonData(
            @RequestBody Map<String, Object> requestBody) {

        logger.info("Received request to /process-json endpoint");

        String projectName = (String) requestBody.get("project_name");
        logger.info("Project Name: {}", projectName);

        List<Map<String, Object>> testCases = (List<Map<String, Object>>) requestBody.get("generated_test_cases");
        logger.info("Number of test cases received: {}", testCases != null ? testCases.size() : 0);
        if (testCases != null) {
            for (int i = 0; i < testCases.size(); i++) {
                logger.info("Test case {}: {}", i + 1, testCases.get(i));
            }
        }

        String excelFilePath;
        try {
            // Generate Excel file using the static method
            excelFilePath = ExcelGeneratorUtil.generateExcel(testCases, excelOutputFolder);
            logger.info("Excel file generated at: {}", excelFilePath);

            // Save to database
            generatedTestCaseService.saveGeneratedTestCase(
                new GeneratedTestCase(projectName, "json", null, null, testCases)
            );
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Test cases generated and stored successfully");
            response.put("test_cases_count", testCases.size());
            response.put("excel_file", excelFilePath.substring(excelFilePath.lastIndexOf("/") + 1));
            response.put("download_url", fileDownloadPrefixUrl + excelFilePath.substring(excelFilePath.lastIndexOf("/") + 1));
            
            return ResponseEntity.ok(response);
        } catch (IOException e) {
            logger.error("Error generating Excel file: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error generating Excel file: " + e.getMessage());
        }
    }

    @GetMapping("/download-excel/{fileName}")
    public ResponseEntity<Resource> downloadGeneratedExcel(@PathVariable String fileName) {
        try {
            Path filePath = Paths.get(excelOutputFolder).resolve(fileName).normalize();
            Resource resource = new UrlResource(filePath.toUri());

            if (!resource.exists()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(null);
            }

            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=" + fileName)
                    .body(resource);

        } catch (IOException e) {
            logger.error("Error while fetching Excel file: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }

    @PostMapping("/upload-and-view")
    public ResponseEntity<?> uploadAndViewFile(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "fileType", required = false) String fileType) {
        
        logger.info("File upload and view request received. File: {}, Type: {}", 
                   file.getOriginalFilename(), fileType);
        
        try {
            // Create upload directory if it doesn't exist
            File uploadDir = new File(fileUploadDirectory);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
                logger.info("Created upload directory: {}", fileUploadDirectory);
            }
            
            // Save the uploaded file
            String fileName = System.currentTimeMillis() + "_" + file.getOriginalFilename();
            File savedFile = new File(uploadDir, fileName);
            file.transferTo(savedFile);
            
            logger.info("File saved successfully: {}", savedFile.getAbsolutePath());
            
            // Generate view URL
            String viewUrl = "/api/view-file/" + fileName;
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "File uploaded successfully");
            response.put("fileName", fileName);
            response.put("originalFileName", file.getOriginalFilename());
            response.put("viewUrl", viewUrl);
            response.put("fileSize", file.getSize());
            response.put("contentType", file.getContentType());
            
            logger.info("File upload response prepared for: {}", fileName);
            return ResponseEntity.ok(response);
            
        } catch (IOException e) {
            logger.error("Error uploading file: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error uploading file: " + e.getMessage());
        }
    }

    @GetMapping("/view-file/{fileName}")
    public ResponseEntity<Resource> viewFile(@PathVariable String fileName) {
        logger.info("File view request received for: {}", fileName);
        
        try {
            Path filePath = Paths.get(fileUploadDirectory).resolve(fileName).normalize();
            Resource resource = new UrlResource(filePath.toUri());
            
            if (!resource.exists()) {
                logger.warn("File not found: {}", fileName);
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(null);
            }
            
            // Determine content type
            String contentType = Files.probeContentType(filePath);
            if (contentType == null) {
                contentType = "application/octet-stream";
            }
            
            logger.info("Serving file: {} with content type: {}", fileName, contentType);
            
            return ResponseEntity.ok()
                    .contentType(MediaType.parseMediaType(contentType))
                    .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + fileName + "\"")
                    .header(HttpHeaders.CACHE_CONTROL, "no-cache, no-store, must-revalidate")
                    .header(HttpHeaders.PRAGMA, "no-cache")
                    .header(HttpHeaders.EXPIRES, "0")
                    .body(resource);
                    
        } catch (IOException e) {
            logger.error("Error serving file {}: {}", fileName, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }

    @GetMapping("/list-uploaded-files")
    public ResponseEntity<List<Map<String, Object>>> listUploadedFiles() {
        logger.info("List uploaded files request received");
        
        try {
            File uploadDir = new File(fileUploadDirectory);
            if (!uploadDir.exists()) {
                logger.info("Upload directory does not exist, returning empty list");
                return ResponseEntity.ok(Collections.emptyList());
            }
            
            File[] files = uploadDir.listFiles();
            if (files == null) {
                logger.info("No files found in upload directory");
                return ResponseEntity.ok(Collections.emptyList());
            }
            
            List<Map<String, Object>> fileList = new ArrayList<>();
            for (File file : files) {
                if (file.isFile()) {
                    Map<String, Object> fileInfo = new HashMap<>();
                    fileInfo.put("fileName", file.getName());
                    fileInfo.put("size", file.length());
                    fileInfo.put("lastModified", file.lastModified());
                    fileInfo.put("viewUrl", "/api/view-file/" + file.getName());
                    fileList.add(fileInfo);
                }
            }
            
            logger.info("Found {} files in upload directory", fileList.size());
            return ResponseEntity.ok(fileList);
            
        } catch (Exception e) {
            logger.error("Error listing uploaded files: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Collections.emptyList());
        }
    }

    @DeleteMapping("/delete-file/{fileName}")
    public ResponseEntity<?> deleteUploadedFile(@PathVariable String fileName) {
        logger.info("Delete file request received for: {}", fileName);
        
        try {
            Path filePath = Paths.get(fileUploadDirectory).resolve(fileName).normalize();
            File file = filePath.toFile();
            
            if (!file.exists()) {
                logger.warn("File not found for deletion: {}", fileName);
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body("File not found: " + fileName);
            }
            
            if (file.delete()) {
                logger.info("File deleted successfully: {}", fileName);
                return ResponseEntity.ok(Map.of("message", "File deleted successfully", "fileName", fileName));
            } else {
                logger.error("Failed to delete file: {}", fileName);
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body("Failed to delete file: " + fileName);
            }
            
        } catch (Exception e) {
            logger.error("Error deleting file {}: {}", fileName, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error deleting file: " + e.getMessage());
        }
    }
}






