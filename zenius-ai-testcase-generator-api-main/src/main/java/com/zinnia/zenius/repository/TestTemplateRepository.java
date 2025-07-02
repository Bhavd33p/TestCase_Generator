package com.zinnia.zenius.repository;

import com.zinnia.zenius.model.TestTemplate;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TestTemplateRepository extends MongoRepository<TestTemplate, String> {

    @Query("{'project_name': ?0}")
    Optional<TestTemplate> findByProjectName(String projectName);

    @Query(value = "{}", fields = "{'project_name': 1, '_id': 0}")
    List<String> findAllProjectNames();

    boolean existsByProjectName(String projectName);

    @Query("{'templateId': ?0}")
    Optional<TestTemplate> findByTemplateId(String templateId);

    boolean existsByTemplateId(String templateId);

    default Optional<TestTemplate> findTemplateOrDefault(String projectName) {
         Optional<TestTemplate> template = findByProjectName(projectName);

        if (template.isEmpty()) {
             Optional<TestTemplate> defaultTemplate = findByTemplateId("default");

            if (defaultTemplate.isPresent()) {
                String defaultProjectName = defaultTemplate.get().getProjectName();
                return findByProjectName(defaultProjectName);
            }
        }
        return template;
    }

}
