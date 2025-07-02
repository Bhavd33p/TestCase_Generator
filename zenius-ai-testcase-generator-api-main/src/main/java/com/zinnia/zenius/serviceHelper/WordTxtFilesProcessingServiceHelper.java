package com.zinnia.zenius.serviceHelper;

import com.zinnia.zenius.utils.DataProcessingUtil;
import org.jsoup.Jsoup;
import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
public class WordTxtFilesProcessingServiceHelper {

         private static final Pattern URL_PATTERN = Pattern.compile("https?://[^\s]+", Pattern.CASE_INSENSITIVE);

        public static String processFile(
                MultipartFile file,
                String jiraBaseUrl,
                String jiraUsername,
                String jiraApiToken,
                String confluenceBaseUrl,
                String confluenceUsername,
                String confluenceApiToken) throws IOException {

            if (file.isEmpty()) {
                return "Uploaded file is empty.";
            }

            String textContent = extractTextFromFile(file);
            Set<String> links = extractUrls(textContent);

            StringBuilder result = new StringBuilder("Extracted Text:\n" + textContent + "\n\n");

            for (String link : links) {
                result.append("\nProcessing link: ").append(link).append("\n");
                if (link.contains("atlassian.net/browse/")) {
                    String issueKey = DataProcessingUtil.extractIdFromLink("jira", link);
                    if (issueKey != null) {
                        result.append("\nJira Data:\n")
                                .append(fetchJiraData(issueKey, jiraBaseUrl, jiraUsername, jiraApiToken));
                    } else {
                        result.append("\nInvalid Jira URL format.\n");
                    }
                } else if (link.contains("atlassian.net/wiki/spaces/")) {
                    String pageId = DataProcessingUtil.extractIdFromLink("confluence", link);
                    if (pageId != null) {
                        result.append("\nConfluence Data:\n")
                                .append(fetchConfluenceData(pageId, confluenceBaseUrl, confluenceUsername, confluenceApiToken));
                    } else {
                        result.append("\nInvalid Confluence URL format.\n");
                    }
                }
            }

            return result.toString();
        }

        private static String extractTextFromFile(MultipartFile file) throws IOException {
            String filename = file.getOriginalFilename();
            if (filename != null && filename.endsWith(".txt")) {
                return extractTextFromTextFile(file);
            } else if (filename != null && filename.endsWith(".docx")) {
                try (InputStream inputStream = file.getInputStream()) {
                    return DataProcessingUtil.extractTextFromDocx(inputStream);
                }
            } else {
                throw new IOException("Unsupported file format. Only .txt and .docx are allowed.");
            }
        }

        private static String extractTextFromTextFile(MultipartFile file) throws IOException {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8))) {
                StringBuilder text = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    text.append(line).append("\n");
                }
                return text.toString();
            }
        }

        private static Set<String> extractUrls(String text) {
            Set<String> links = new HashSet<>();
            Matcher matcher = URL_PATTERN.matcher(text);
            while (matcher.find()) {
                links.add(matcher.group());
            }
            return links;
        }

        private static String fetchJiraData(String issueKey, String baseUrl, String username, String apiToken) throws IOException {
            String apiUrl = baseUrl + "/rest/api/3/issue/" + issueKey;
            String jsonResponse = fetchData(apiUrl, username, apiToken);

            JSONObject json = new JSONObject(jsonResponse);
            JSONObject fields = json.getJSONObject("fields");

            String summary = fields.optString("summary", "No summary available.");
            String description = fields.optString("description", "No description available.");
            String cleanDescription = Jsoup.parse(description).text();

            StringBuilder attachmentsInfo = new StringBuilder();
            if (fields.has("attachment")) {
                JSONArray attachments = fields.getJSONArray("attachment");
                for (int i = 0; i < attachments.length(); i++) {
                    JSONObject attachment = attachments.getJSONObject(i);
                    attachmentsInfo.append("\nAttachment: ").append(attachment.getString("filename"))
                            .append("\nDownload: ").append(attachment.getString("content"));
                }
            }

            return "Jira Summary: " + summary + "\n\nJira Description: " + cleanDescription + "\n\n" + attachmentsInfo;
        }

        private static String fetchConfluenceData(String pageId, String baseUrl, String username, String apiToken) throws IOException {
            String apiUrl = baseUrl + "/rest/api/content/" + pageId + "?expand=body.storage";
            String jsonResponse = fetchData(apiUrl, username, apiToken);

            JSONObject json = new JSONObject(jsonResponse);
            String htmlContent = json.getJSONObject("body").getJSONObject("storage").optString("value", "No content available.");
            return "Confluence Page Content:\n" + Jsoup.parse(htmlContent).text();
        }

        private static String fetchData(String urlString, String username, String apiToken) throws IOException {
            URL url = new URL(urlString);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            String encodedAuth = Base64.getEncoder().encodeToString((username + ":" + apiToken).getBytes());
            connection.setRequestProperty("Authorization", "Basic " + encodedAuth);
            connection.setRequestProperty("Accept", "application/json");

            int responseCode = connection.getResponseCode();
            if (responseCode != 200) {
                return "Failed to fetch data from " + urlString + ". HTTP response code: " + responseCode;
            }

            try (BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream(), StandardCharsets.UTF_8))) {
                StringBuilder response = new StringBuilder();
                String inputLine;
                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }
                return response.toString();
            }
        }
    }
