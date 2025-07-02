# 🔐 Security Setup Guide

This document explains how to set up API keys and sensitive configuration for the Zenius AI Test Case Generator.

## ⚠️ Important Security Notice

**API keys and sensitive credentials should NEVER be committed to the repository.** This project uses template files to help you set up your configuration safely.

## 🚀 Quick Setup

### 1. Copy Template Files

Copy the template files and remove the `.template` extension:

```bash
# For NLP service
cp zenius_testcase_generator_nlp-main/application.properties.template zenius_testcase_generator_nlp-main/application.properties
cp zenius_testcase_generator_nlp-main/config.yaml.template zenius_testcase_generator_nlp-main/config.yaml
cp zenius_testcase_generator_nlp-main/src/utilities/config.json.template zenius_testcase_generator_nlp-main/src/utilities/config.json

# For Java API service
cp zenius-ai-testcase-generator-api-main/src/main/resources/application.properties.template zenius-ai-testcase-generator-api-main/src/main/resources/application.properties
```

### 2. Configure API Keys

#### OpenAI API Key
Replace `YOUR_OPENAI_API_KEY` with your actual OpenAI API key in:
- `zenius_testcase_generator_nlp-main/config.yaml`
- `zenius_testcase_generator_nlp-main/src/utilities/config.json`

#### Jira & Confluence API Tokens
Replace the following placeholders in both application.properties files:
- `YOUR_JIRA_API_TOKEN` - Your Jira API token
- `YOUR_CONFLUENCE_API_TOKEN` - Your Confluence API token
- `your-domain.atlassian.net` - Your Atlassian domain
- `your-email@domain.com` - Your email address

#### MongoDB Connection
Replace `YOUR_USERNAME:YOUR_PASSWORD@your-cluster.mongodb.net` with your actual MongoDB connection details.

## 🔑 How to Get API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### Jira/Confluence API Token
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create a new API token
3. Copy the token

### MongoDB Atlas
1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a cluster or use existing one
3. Get the connection string from "Connect" button
4. Replace username and password in the connection string

## 🛡️ Environment Variables (Alternative)

Instead of hardcoding API keys, you can use environment variables:

### For Windows (CMD):
```cmd
set OPENAI_API_KEY=your-api-key-here
set JIRA_API_TOKEN=your-jira-token-here
set CONFLUENCE_API_TOKEN=your-confluence-token-here
```

### For Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
$env:JIRA_API_TOKEN="your-jira-token-here"
$env:CONFLUENCE_API_TOKEN="your-confluence-token-here"
```

### For Linux/macOS:
```bash
export OPENAI_API_KEY="your-api-key-here"
export JIRA_API_TOKEN="your-jira-token-here"
export CONFLUENCE_API_TOKEN="your-confluence-token-here"
```

## ✅ Verification

After setting up your configuration files, verify they work:

1. Start the services
2. Check logs for any authentication errors
3. Test API endpoints

## 🚫 What's Ignored by Git

The following files are automatically ignored by git:
- `application.properties`
- `config.yaml`
- `config.json`
- `*.env`
- `*secrets*`
- `*api-keys*`

## 🆘 Troubleshooting

### "API key not found" error
- Check that you copied the template files correctly
- Verify API keys are not empty or contain placeholder text
- Ensure no extra spaces around the API key

### "Invalid API key" error
- Verify the API key is correct and active
- Check if the API key has required permissions
- Ensure the API key format is correct (OpenAI keys start with `sk-`)

### "Connection refused" errors
- Check MongoDB connection string
- Verify network connectivity
- Ensure services are running on correct ports

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Verify all template files are copied and configured
3. Check application logs for specific error messages
4. Ensure all services are running on expected ports 