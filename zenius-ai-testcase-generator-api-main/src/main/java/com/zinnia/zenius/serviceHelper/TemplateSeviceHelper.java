package com.zinnia.zenius.serviceHelper;
import com.zinnia.zenius.model.TestTemplate;
import com.zinnia.zenius.repository.TestTemplateRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class TemplateSeviceHelper {


        private static final Logger logger = LoggerFactory.getLogger(TemplateSeviceHelper.class);

        public static Optional<TestTemplate> getTemplateByProjectName(TestTemplateRepository repository, String projectName) {
            logger.info("Searching for project name: {}", projectName);
            Optional<TestTemplate> template = repository.findByProjectName(projectName);

            if (template.isPresent()) {
                logger.info("Template Found: {}", template.get());
            } else {
                logger.warn("No template found for project: {}", projectName);
            }
            return template;
        }

        public static List<String> getAllProjectNames(TestTemplateRepository repository) {
            return repository.findAllProjectNames()
                    .stream()
                    .distinct()
                    .collect(Collectors.toList());
        }

        public static boolean existsByProjectName(TestTemplateRepository repository, String projectName) {
            return repository.existsByProjectName(projectName);
        }

        public static boolean existsByTemplateId(TestTemplateRepository repository, String templateId) {
            return repository.existsByTemplateId(templateId);
        }

        public static void saveTemplate(TestTemplateRepository repository, TestTemplate testTemplate) {
            if (repository.existsByProjectName(testTemplate.getProjectName())) {
                throw new IllegalArgumentException("Template for project already exists.");
            }
            if (repository.existsByTemplateId(testTemplate.getTemplateId())) {
                throw new IllegalArgumentException("Template ID already exists.");
            }
            repository.save(testTemplate);
            logger.info("Template saved successfully!");
        }

        public static Optional<TestTemplate> findTemplateOrDefault(TestTemplateRepository repository, String projectName) {
            Optional<TestTemplate> template = repository.findByProjectName(projectName);

            if (template.isEmpty()) {
                template = repository.findByTemplateId("default");
            }

            return template;
        }
    }
