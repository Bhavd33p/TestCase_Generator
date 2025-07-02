package com.zinnia.zenius.service;

import com.zinnia.zenius.serviceHelper.GeneratedTestCaseServiceHelper;
import com.zinnia.zenius.model.GeneratedTestCase;
import com.zinnia.zenius.repository.GeneratedTestCaseRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class GeneratedTestCaseService {

    private final GeneratedTestCaseServiceHelper generatedTestCaseServiceHelper;

    public GeneratedTestCaseService(GeneratedTestCaseRepository generatedTestCaseRepository) {
        this.generatedTestCaseServiceHelper = new GeneratedTestCaseServiceHelper(generatedTestCaseRepository);
    }

    public GeneratedTestCase saveGeneratedTestCase(GeneratedTestCase testCase) {
        return generatedTestCaseServiceHelper.saveGeneratedTestCase(testCase);
    }

    public Optional<GeneratedTestCase> findBySourceAndIdentifier(String source, String identifier) {
        return generatedTestCaseServiceHelper.findBySourceAndIdentifier(source, identifier);
    }
}
