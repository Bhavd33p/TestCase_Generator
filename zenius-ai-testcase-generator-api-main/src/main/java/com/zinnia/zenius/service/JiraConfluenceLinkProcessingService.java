package com.zinnia.zenius.service;

import com.zinnia.zenius.serviceHelper.JiraConfluenceLinkProcessingServiceHelper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class JiraConfluenceLinkProcessingService {

    @Value("${jira.base.url}")
    private String jiraBaseUrl;

    @Value("${jira.username}")
    private String jiraUsername;

    @Value("${jira.api.token}")
    private String jiraApiToken;

    @Value("${confluence.base.url}")
    private String confluenceBaseUrl;

    @Value("${confluence.username}")
    private String confluenceUsername;

    @Value("${confluence.api.token}")
    private String confluenceApiToken;

    private final JiraConfluenceLinkProcessingServiceHelper helper = new JiraConfluenceLinkProcessingServiceHelper();

    public Map<String, Object> fetchData(String link) {
        if (link.contains("atlassian.net/browse/")) {
            return helper.fetchJiraData(link, jiraBaseUrl, jiraUsername, jiraApiToken);
        } else if (link.contains("atlassian.net/wiki/spaces/")) {
            return helper.fetchConfluenceData(link, confluenceBaseUrl, confluenceUsername, confluenceApiToken);
        } else {
            throw new IllegalArgumentException("Please provide a valid Jira or Confluence link.");
        }
    }
}
