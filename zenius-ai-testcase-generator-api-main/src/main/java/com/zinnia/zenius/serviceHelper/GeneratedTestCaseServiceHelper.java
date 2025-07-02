package com.zinnia.zenius.serviceHelper;
import com.zinnia.zenius.model.GeneratedTestCase;
import com.zinnia.zenius.repository.GeneratedTestCaseRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Optional;

public class GeneratedTestCaseServiceHelper {
    private static final Logger logger = LoggerFactory.getLogger(GeneratedTestCaseServiceHelper.class);

    private final GeneratedTestCaseRepository generatedTestCaseRepository;

    public GeneratedTestCaseServiceHelper(GeneratedTestCaseRepository generatedTestCaseRepository) {
        this.generatedTestCaseRepository = generatedTestCaseRepository;
    }

    public GeneratedTestCase saveGeneratedTestCase(GeneratedTestCase testCase) {
        logger.info("Saving generated test case for project: {}", testCase.getProjectName());
        return generatedTestCaseRepository.save(testCase);
    }

    public Optional<GeneratedTestCase> findBySourceAndIdentifier(String source, String identifier) {
        List<GeneratedTestCase> testCases;

        if (source.equalsIgnoreCase("jira") || source.equalsIgnoreCase("confluence")) {
            testCases = generatedTestCaseRepository.findBySourceAndJiraOrConfluenceId(source, identifier);
        } else {
            testCases = generatedTestCaseRepository.findBySourceAndHash(source, identifier);
        }

        if (testCases.isEmpty()) {
            return Optional.empty();
        } else if (testCases.size() == 1) {
            logger.info("Single test case found for source: {}, identifier: {}", source, identifier);
            return Optional.of(testCases.get(0));
        } else {
            logger.info("Multiple test cases found for source: {}, identifier: {}. Returning the latest one.", source, identifier);
            return Optional.of(testCases.get(0));
        }
    }

}

