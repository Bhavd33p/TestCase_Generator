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
import com.zinnia.zenius.utils.MultipartFileResource;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

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

    @Value("${excel.output.folder}")
    private String excelOutputFolder;

    @Value("${fastapi.token.limit}")
    private int tokenLimit;

    @Value("${file.download.prefix.url}")
    private String fileDownloadPrefixUrl;

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

    @PostMapping("/process/{source}")
    public ResponseEntity<?> processFileOrLink(
            @PathVariable("source") String source,
            @RequestParam(value = "file", required = false) MultipartFile file,
            @RequestParam(value = "link", required = false) String link,
            @RequestParam(value = "modelName") String modelName,
            @RequestParam(value = "projectName") String projectName,
            @RequestParam(value = "icdFile" ) MultipartFile icdFile,
            @RequestParam(value = "swadFile" ) MultipartFile swadFile,
            @RequestParam(value = "plainText", required = false) String plainText) {
        
        File tempPdfFile = null;
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
                logger.info("Plain Text Input provided");
            } else {
                logger.info("No plain text input received.");
            }

            // Extract text based on source type
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

            // Check if test cases already exist
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

            // Step 1: Embed SWAD and ICD documents first
            logger.info("Step 1: Embedding SWAD and ICD documents");
            try {
                HttpHeaders embedHeaders = new HttpHeaders();
                embedHeaders.setContentType(MediaType.MULTIPART_FORM_DATA);
                MultiValueMap<String, Object> embedReq = new LinkedMultiValueMap<>();
                embedReq.add("swadFile", new MultipartFileResource(swadFile));
                embedReq.add("icdFile", new MultipartFileResource(icdFile));
                embedReq.add("project_name", projectName);
                embedReq.add("model_name", modelName);

                HttpEntity<MultiValueMap<String, Object>> embedEntity = new HttpEntity<>(embedReq, embedHeaders);
                
                // Correct FastAPI endpoint for embedding documents
                String embedUrl = fastApiTestCasesBaseUrl + "/embed-documents/" + source;
                logger.info("Embedding SWAD/ICD documents — POST {}", embedUrl);
                
                ResponseEntity<String> embedResponse = restTemplate.postForEntity(embedUrl, embedEntity, String.class);
                if (embedResponse.getStatusCode().is2xxSuccessful()) {
                    logger.info("Successfully embedded SWAD and ICD documents");
                } else {
                    logger.warn("Document embedding returned status: {}", embedResponse.getStatusCode());
                }
            } catch (Exception e) {
                logger.error("Error embedding documents: {}", e.getMessage(), e);
                // Continue with test case generation even if embedding fails
            }

            // Step 2: Generate test cases from requirements
            logger.info("Step 2: Generating test cases from requirements");
            tempPdfFile = PdfGeneratorUtil.createPdfFromText(extractedText, excelOutputFolder, "temp_input_" + System.currentTimeMillis() + ".pdf");
            int pageCount = PdfGeneratorUtil.getPageCount(tempPdfFile);
            logger.info("Generated PDF has {} pages", pageCount);

            MultiValueMap<String, Object> multipartRequest = new LinkedMultiValueMap<>();
            multipartRequest.add("file", new FileSystemResource(tempPdfFile));
            multipartRequest.add("project_name", projectName);
            multipartRequest.add("model_name", modelName);
            multipartRequest.add("template_columns", objectMapper.writeValueAsString(templateColumns));
            multipartRequest.add("source_id", source.matches("jira|confluence") ? uniqueIdentifier : null);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(multipartRequest, headers);
            
            // Correct FastAPI endpoint for test case generation
            String testCaseUrl = fastApiTestCasesBaseUrl + "/generate-test-cases/" + source;
            logger.info("Generating test cases — POST {}", testCaseUrl);
            logger.info("Request Body parts: {}", requestEntity.getBody().keySet());

            ResponseEntity<String> responseEntity = restTemplate.postForEntity(testCaseUrl, requestEntity, String.class);
            String responseBody = responseEntity.getBody();
            logger.info("FastAPI Response Status: {}", responseEntity.getStatusCode());
            logger.info("FastAPI Raw Response: {}", responseBody);

            if (!responseEntity.getStatusCode().is2xxSuccessful()) {
                logger.error("FastAPI returned error status: {}", responseEntity.getStatusCode());
                return ResponseEntity.status(responseEntity.getStatusCode())
                    .body("Error from FastAPI: " + responseBody);
            }

            // Parse the response
            JsonNode rootNode = objectMapper.readTree(responseBody);
            JsonNode testCasesNode = rootNode.path("test_cases");

            if (testCasesNode.isMissingNode() || !testCasesNode.isArray()) {
                logger.error("Invalid test case format received from FastAPI.");
                logger.error("Response structure: {}", rootNode.toPrettyString());
                return ResponseEntity.badRequest().body("Invalid test case format received from FastAPI.");
            }

            List<Map<String, Object>> testCases = new ArrayList<>();
            for (JsonNode node : testCasesNode) {
                testCases.add(objectMapper.convertValue(node, new TypeReference<>() {}));
            }

            if (testCases.isEmpty()) {
                logger.warn("No test cases generated from FastAPI");
                return ResponseEntity.ok(Map.of(
                    "message", "No test cases were generated. Please check your requirements.",
                    "test_cases_count", 0
                ));
            }

            // Generate Excel file
            String excelFilePath = excelGeneratorUtil.generateExcel(testCases, excelOutputFolder);
            logger.info("Excel file generated: {}", excelFilePath);

            // Save to database
            generatedTestCaseService.saveGeneratedTestCase(
                    new GeneratedTestCase(projectName, source,
                            source.matches("jira|confluence") ? uniqueIdentifier : null,
                            source.matches("word|text|plaintext") ? uniqueIdentifier : null,
                            testCases)
            );

            Map<String, Object> response = new HashMap<>();
            response.put("message", "Test cases generated and stored successfully");
            response.put("test_cases_count", testCases.size());
            response.put("excel_file", excelFilePath.substring(excelFilePath.lastIndexOf("/") + 1));
            response.put("download_url", fileDownloadPrefixUrl + excelFilePath.substring(excelFilePath.lastIndexOf("/") + 1));

            logger.info("Successfully generated {} test cases", testCases.size());
            return ResponseEntity.ok(response);

        } catch (RestClientException e) {
            logger.error("Error communicating with FastAPI: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                .body("Error communicating with FastAPI: " + e.getMessage());
        } catch (IOException e) {
            logger.error("Error processing request: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Error processing request: " + e.getMessage());
        } catch (Exception e) {
            logger.error("Unexpected error: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Unexpected error: " + e.getMessage());
        } finally {
            // Clean up temporary PDF file
            if (tempPdfFile != null && tempPdfFile.exists()) {
                try {
                    boolean deleted = tempPdfFile.delete();
                    if (deleted) {
                        logger.info("Temporary PDF file deleted: {}", tempPdfFile.getName());
                    } else {
                        logger.warn("Failed to delete temporary PDF file: {}", tempPdfFile.getName());
                    }
                } catch (Exception e) {
                    logger.error("Error deleting temporary PDF file: {}", e.getMessage(), e);
                }
            }
        }
    }

    @GetMapping("/download-excel/{fileName}")
    public ResponseEntity<Resource> downloadGeneratedExcel(@PathVariable String fileName) {
        try {
            Path filePath = Paths.get(excelOutputFolder).resolve(fileName).normalize();
            Resource resource = new UrlResource(filePath.toUri());

            if (!resource.exists()) {
                logger.error("Excel file not found: {}", fileName);
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(null);
            }

            logger.info("Downloading Excel file: {}", fileName);
            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + fileName + "\"")
                    .body(resource);

        } catch (IOException e) {
            logger.error("Error while fetching Excel file: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }
} 