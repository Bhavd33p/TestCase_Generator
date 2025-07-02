package com.zinnia.zenius.controller;

import com.zinnia.zenius.model.TestTemplate;
import com.zinnia.zenius.service.TemplateService;
import com.zinnia.zenius.utils.DataProcessingUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.core.io.Resource;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "${frontend.url}")

public class TemplateController {

    private static final Logger logger = LoggerFactory.getLogger(TemplateController.class);
    private final TemplateService templateService;

    @Value("${sample.template.path}")
    private String sampleTemplatePath;

    @Value("${sample.template.filename}")
    private String sampleTemplateFilename;

    @Autowired
    public TemplateController(TemplateService templateService) {
        this.templateService = templateService;
    }

    @GetMapping("/projects")
    public List<String> getAllProjectNames() {
        return templateService.getAllProjectNames();
    }

    @GetMapping("/download-template")
    public ResponseEntity<InputStreamResource> downloadSampleTemplate() {
        try {
            Resource resource = new ClassPathResource(sampleTemplatePath);
            InputStream inputStream = resource.getInputStream();

            HttpHeaders headers = new HttpHeaders();
            headers.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=" + sampleTemplateFilename);

            return ResponseEntity.ok()
                    .headers(headers)
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .body(new InputStreamResource(inputStream));

        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(null);
        }
    }

    @PostMapping("/create-template")
    public ResponseEntity<?> createTemplate(
            @RequestParam("file") MultipartFile file,
            @RequestParam("templateId") String templateId,
            @RequestParam("projectName") String projectName) {

        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("File is required.");
        }

        if (templateService.existsByProjectName(projectName)) {
            return ResponseEntity.badRequest().body("Template for project already exists.");
        }
        if (templateService.existsByTemplateId(templateId)) {
            return ResponseEntity.badRequest().body("Template ID already exists.");
        }
        List<String> extractedColumns;
        try {
            extractedColumns = DataProcessingUtil.extractColumnsFromFile(file);
        } catch (IOException e) {
            logger.error("Error reading file: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error reading file.");
        }

        if (extractedColumns.isEmpty()) {
            return ResponseEntity.badRequest().body("No columns found in the file.");
        }

        TestTemplate testTemplate = new TestTemplate();
        testTemplate.setTemplateId(templateId);
        testTemplate.setProjectName(projectName);
        testTemplate.setColumns(extractedColumns);

        templateService.saveTemplate(testTemplate);
        logger.info("Template for project '{}' created successfully.", projectName);

        return ResponseEntity.ok("Template created successfully.");
    }



}
