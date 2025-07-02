package com.zinnia.zenius.serviceHelper;
import com.zinnia.zenius.utils.DataProcessingUtil;
import org.jsoup.Jsoup;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.*;
public class JiraConfluenceLinkProcessingServiceHelper  {

        private final RestTemplate restTemplate = new RestTemplate();

        public Map<String, Object> fetchJiraData(String jiraLink, String jiraBaseUrl, String jiraUsername, String jiraApiToken) {
            String issueKey = DataProcessingUtil.extractIdFromLink("jira", jiraLink);
            String apiUrl = jiraBaseUrl + "/rest/api/2/issue/" + issueKey;

            HttpHeaders headers = new HttpHeaders();
            headers.setBasicAuth(jiraUsername, jiraApiToken);
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<String> entity = new HttpEntity<>(headers);
            ResponseEntity<Map> response = restTemplate.exchange(apiUrl, HttpMethod.GET, entity, Map.class);
            Map<String, Object> issueData = response.getBody();
            if (issueData == null) return Collections.emptyMap();

            Map<String, Object> fields = (Map<String, Object>) issueData.get("fields");
            if (fields == null) return Collections.emptyMap();

            List<Map<String, String>> attachmentsData = processAttachments(fetchJiraAttachments(issueData), jiraUsername, jiraApiToken);

            Map<String, Object> refinedData = new HashMap<>();
            refinedData.put("issueKey", issueData.get("key"));
            refinedData.put("summary", fields.get("summary"));
            refinedData.put("description", fields.get("description"));
            refinedData.put("attachmentsData", attachmentsData);

            return refinedData;
        }

        public Map<String, Object> fetchConfluenceData(String confluenceLink, String confluenceBaseUrl, String confluenceUsername, String confluenceApiToken) {
            String pageId = DataProcessingUtil.extractIdFromLink("confluence", confluenceLink);
            String apiUrl = confluenceBaseUrl + "/rest/api/content/" + pageId + "?expand=body.storage,children.attachment";

            HttpHeaders headers = new HttpHeaders();
            headers.setBasicAuth(confluenceUsername, confluenceApiToken);
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<String> entity = new HttpEntity<>(headers);
            ResponseEntity<Map> response = restTemplate.exchange(apiUrl, HttpMethod.GET, entity, Map.class);
            Map<String, Object> pageData = response.getBody();
            if (pageData == null) return Collections.emptyMap();

            Map<String, Object> storage = (Map<String, Object>) ((Map<String, Object>) pageData.get("body")).get("storage");
            String contentHtml = (String) storage.get("value");
            String plainTextContent = Jsoup.parse(contentHtml).text();

            List<Map<String, String>> attachmentsData = processAttachments(fetchConfluenceAttachments(pageData, confluenceBaseUrl), confluenceUsername, confluenceApiToken);

            Map<String, Object> refinedData = new HashMap<>();
            refinedData.put("pageId", pageData.get("id"));
            refinedData.put("title", pageData.get("title"));
            refinedData.put("description", plainTextContent);
            refinedData.put("attachmentsData", attachmentsData);

            return refinedData;
        }

        private List<Map<String, String>> fetchJiraAttachments(Map<String, Object> issueData) {
            List<Map<String, String>> attachmentData = new ArrayList<>();
            Map<String, Object> fields = (Map<String, Object>) issueData.get("fields");

            if (fields != null && fields.containsKey("attachment")) {
                List<Map<String, Object>> attachments = (List<Map<String, Object>>) fields.get("attachment");
                for (Map<String, Object> attachment : attachments) {
                    attachmentData.add(Map.of(
                            "filename", (String) attachment.get("filename"),
                            "url", (String) attachment.get("content")
                    ));
                }
            }
            return attachmentData;
        }

        private List<Map<String, String>> fetchConfluenceAttachments(Map<String, Object> pageData, String confluenceBaseUrl) {
            List<Map<String, String>> attachmentData = new ArrayList<>();
            Map<String, Object> children = (Map<String, Object>) pageData.get("children");

            if (children != null && children.containsKey("attachment")) {
                Map<String, Object> attachments = (Map<String, Object>) children.get("attachment");
                List<Map<String, Object>> results = (List<Map<String, Object>>) attachments.get("results");
                for (Map<String, Object> attachment : results) {
                    Map<String, Object> _links = (Map<String, Object>) attachment.get("_links");
                    attachmentData.add(Map.of(
                            "filename", (String) attachment.get("title"),
                            "url", confluenceBaseUrl + _links.get("download")
                    ));
                }
            }
            return attachmentData;
        }

        private List<Map<String, String>> processAttachments(List<Map<String, String>> attachments, String username, String token) {
            List<Map<String, String>> extractedData = new ArrayList<>();

            for (Map<String, String> attachment : attachments) {
                String filename = attachment.get("filename");
                String fileUrl = attachment.get("url");

                if (!filename.toLowerCase().matches(".*\\.(docx|txt|pdf|xlsx)$")) {
                    continue;
                }

                File tempFile = new File(System.getProperty("java.io.tmpdir"), filename);
                downloadFile(fileUrl, tempFile, filename, username, token);

                String extractedText = "Failed to extract text.";
                try (FileInputStream fis = new FileInputStream(tempFile)) {
                    if (filename.endsWith(".txt")) {
                        extractedText = new String(fis.readAllBytes(), StandardCharsets.UTF_8);
                    } else if (filename.endsWith(".docx")) {
                        extractedText = DataProcessingUtil.extractTextFromDocx(fis);
                    } else if (filename.endsWith(".pdf")) {
                        extractedText = DataProcessingUtil.extractTextFromPdf(fis);
                    } else if (filename.endsWith(".xlsx")) {
                        extractedText = DataProcessingUtil.extractTextFromExcel(fis);
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                } finally {
                    if (tempFile.exists()) tempFile.delete();
                }

                extractedData.add(Map.of("filename", filename, "content", extractedText));
            }

            return extractedData;
        }

        private void downloadFile(String fileUrl, File destinationFile, String filename, String username, String token) {
            try {
                URL url = new URL(fileUrl);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();

                String auth = username + ":" + token;
                String encodedAuth = Base64.getEncoder().encodeToString(auth.getBytes(StandardCharsets.UTF_8));
                connection.setRequestProperty("Authorization", "Basic " + encodedAuth);
                connection.setRequestMethod("GET");
                connection.connect();

                try (InputStream input = connection.getInputStream(); FileOutputStream output = new FileOutputStream(destinationFile)) {
                    byte[] buffer = new byte[1024];
                    int bytesRead;
                    while ((bytesRead = input.read(buffer)) != -1) {
                        output.write(buffer, 0, bytesRead);
                    }
                }

            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
