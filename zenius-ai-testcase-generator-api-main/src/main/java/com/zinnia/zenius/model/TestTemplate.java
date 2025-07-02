package com.zinnia.zenius.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.util.List;

@Document(collection = "test_template")
public class TestTemplate {

    @Id
    private String id;
    @Field("template_id")

    private String templateId;
    @Field("project_name")

    private String projectName;

    private List<String> columns;

    public TestTemplate() {
    }

    public TestTemplate(String projectName, List<String> columns) {
        this.projectName = projectName;
        this.columns = columns;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }
    public String getTemplateId() {
        return templateId;
    }

    public void setTemplateId(String templateId) {
        this.templateId = templateId;
    }
    public String getProjectName() {
        return projectName;
    }

    public void setProjectName(String projectName) {
        this.projectName = projectName;
    }

    public List<String> getColumns() {
        return columns;
    }

    public void setColumns(List<String> columns) {
        this.columns = columns;
    }

    @Override
    public String toString() {
        return "TestTemplate{" +
                "id='" + id + '\'' +
                ", projectName='" + projectName + '\'' +
                ", columns=" + columns +
                '}';
    }
}
