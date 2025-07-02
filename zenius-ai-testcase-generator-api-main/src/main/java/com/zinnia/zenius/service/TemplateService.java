package com.zinnia.zenius.service;

import com.zinnia.zenius.serviceHelper.TemplateSeviceHelper;
import com.zinnia.zenius.model.TestTemplate;
import com.zinnia.zenius.repository.TestTemplateRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class TemplateService {

    private final TestTemplateRepository testTemplateRepository;

    public TemplateService(TestTemplateRepository testTemplateRepository) {
        this.testTemplateRepository = testTemplateRepository;
    }

    public Optional<TestTemplate> getTemplateByProjectName(String projectName) {
        return TemplateSeviceHelper.getTemplateByProjectName(testTemplateRepository, projectName);
    }

    public List<String> getAllProjectNames() {
        return TemplateSeviceHelper.getAllProjectNames(testTemplateRepository);
    }

    public boolean existsByProjectName(String projectName) {
        return TemplateSeviceHelper.existsByProjectName(testTemplateRepository, projectName);
    }

    public boolean existsByTemplateId(String templateId) {
        return TemplateSeviceHelper.existsByTemplateId(testTemplateRepository, templateId);
    }

    public void saveTemplate(TestTemplate testTemplate) {
        TemplateSeviceHelper.saveTemplate(testTemplateRepository, testTemplate);
    }

    public Optional<TestTemplate> findTemplateOrDefault(String projectName) {
        return TemplateSeviceHelper.findTemplateOrDefault(testTemplateRepository, projectName);
    }
}
