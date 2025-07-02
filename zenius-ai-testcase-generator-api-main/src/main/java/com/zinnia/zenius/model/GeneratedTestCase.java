package com.zinnia.zenius.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.TypeAlias;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.List;
import java.util.Map;

@Document(collection = "generated_test_cases")
@TypeAlias("GeneratedTestCase")
public class GeneratedTestCase {

    @Id
    private String id;

    private String projectName;
    private String source;
    private String sourceId;
    private String hash;
    private List<Map<String, Object>> generatedTestCases;

    public GeneratedTestCase() {
    }

    public GeneratedTestCase(String projectName, String source, String sourceId, String hash, List<Map<String, Object>> generatedTestCases) {
        this.projectName = projectName;
        this.source = source;
        this.sourceId = sourceId;
        this.hash = hash;
        this.generatedTestCases = generatedTestCases;
    }
    public List<Map<String, Object>> getTestCases() {
        return generatedTestCases;
    }
    public String getId() {
        return id;
    }

    public String getProjectName() {
        return projectName;
    }

    public String getSource() {
        return source;
    }

    public String getSourceId() {
        return sourceId;
    }

    public String getHash() {
        return hash;
    }

    public List<Map<String, Object>> getGeneratedTestCases() {
        return generatedTestCases;
    }

    @Override
    public String toString() {
        return "GeneratedTestCase{" +
                "id='" + id + '\'' +
                ", projectName='" + projectName + '\'' +
                ", source='" + source + '\'' +
                ", sourceId='" + sourceId + '\'' +
                ", hash='" + hash + '\'' +
                ", generatedTestCases=" + generatedTestCases +
                '}';
    }
}
