package com.zinnia.zenius.service;

import com.zinnia.zenius.serviceHelper.WordTxtFilesProcessingServiceHelper;
import com.zinnia.zenius.utils.DataProcessingUtil;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Service
public class WordTxtFilesProcessingService {

    @Value("${jira.username}")
    private String jiraUsername;

    @Value("${jira.api.token}")
    private String jiraApiToken;

    @Value("${jira.base.url}")
    private String jiraBaseUrl;

    @Value("${confluence.base.url}")
    private String confluenceBaseUrl;

    @Value("${confluence.username}")
    private String confluenceUsername;

    @Value("${confluence.api.token}")
    private String confluenceApiToken;

    public String processFile(MultipartFile file) throws IOException {
        return WordTxtFilesProcessingServiceHelper.processFile(
                file,
                jiraBaseUrl,
                jiraUsername,
                jiraApiToken,
                confluenceBaseUrl,
                confluenceUsername,
                confluenceApiToken
        );
    }

}
