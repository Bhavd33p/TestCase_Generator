# 📊 How to View Allure Reports - Complete Guide

## 🚨 Current Issue
The Gradle wrapper has a corrupted download. Here are multiple ways to view your Allure reports:

## 🛠️ Method 1: Fix Gradle Wrapper (Recommended)

### Step 1: Clean Gradle Cache
```bash
# Delete the corrupted Gradle distribution
rmdir /s /q "%USERPROFILE%\.gradle\wrapper\dists\gradle-8.11.1-bin"

# Or manually delete this folder:
# C:\Users\singhbh\.gradle\wrapper\dists\gradle-8.11.1-bin\
```

### Step 2: Re-download Gradle
```bash
cd zenius-ai-testcase-generator-api-main
gradlew.bat wrapper --gradle-version 8.11.1
```

### Step 3: Run Tests and Generate Report
```bash
gradlew.bat clean test allureReport serveAllureReport
```

## 🔧 Method 2: Install Allure CLI Directly

### Option A: Using Chocolatey (Recommended for Windows)
```bash
# Install Chocolatey first if you don't have it
# Then install Allure
choco install allure
```

### Option B: Using npm
```bash
npm install -g allure-commandline
```

### Option C: Manual Download
1. Go to: https://github.com/allure-framework/allure2/releases
2. Download the latest `allure-x.x.x.zip`
3. Extract to a folder (e.g., `C:\allure`)
4. Add `C:\allure\bin` to your PATH environment variable

### After Installing Allure CLI:
```bash
cd zenius-ai-testcase-generator-api-main

# If you have existing test results
allure serve build/allure-results

# Or generate a static report
allure generate build/allure-results -o build/allure-report --clean
```

## 📂 Method 3: View Existing Reports (If Any)

### Check for Existing Reports:
1. Navigate to: `zenius-ai-testcase-generator-api-main\build\reports\allure-report\`
2. If the folder exists, open `index.html` in your browser

### Check for Test Results:
1. Navigate to: `zenius-ai-testcase-generator-api-main\build\allure-results\`
2. If JSON files exist, you can generate reports from them

## 🚀 Method 4: Quick Demo Report

Since we have comprehensive test cases, let me create a demo report structure:
```
build/
├── allure-results/
│   ├── test-cases.json
│   ├── environment.properties
│   └── categories.json
└── reports/
    └── allure-report/
        └── index.html
```

## 📋 Step-by-Step Instructions

### **For Immediate Viewing:**

1. **Install Allure CLI** (Choose one):
   ```bash
   # Using Chocolatey (easiest)
   choco install allure
   
   # Using npm
   npm install -g allure-commandline
   ```

2. **Verify Installation**:
   ```bash
   allure --version
   ```

3. **Generate Test Results** (if needed):
   ```bash
   # You can run tests manually or use IDE
   # The test results will be in build/allure-results/
   ```

4. **View Report**:
   ```bash
   cd zenius-ai-testcase-generator-api-main
   allure serve build/allure-results
   ```

## 🌐 What You'll See in the Report

### **Dashboard Overview:**
- ✅ **Test Statistics**: Total, Passed, Failed, Skipped
- 📊 **Execution Timeline**: When tests ran
- 🏷️ **Categories**: Our custom failure categories
- 📈 **Trends**: Success rates over time

### **Test Details:**
- 📝 **Epic**: "Zenius AI Test Case Generator"
- 🎯 **Features**: "Data Processing Controller", "Application Context"
- 📚 **Stories**: "File Upload and Viewing", "File Management", etc.
- 🏃 **Steps**: Detailed step-by-step execution with `Allure.step()`

### **Categories We've Configured:**
- 🔄 **File Upload Issues**
- 👁️ **File Viewing Issues**
- 🌐 **API Connection Issues**
- 💾 **Database Issues**
- 🔐 **Authentication Issues**
- ⚙️ **Configuration Issues**

## 🔍 Test Cases Included

Our test suite includes:

### **File Management Tests:**
- ✅ Upload and View File - Success
- ❌ Upload File - Null File (Error Handling)
- ✅ View File - Success
- ❌ View File - File Not Found
- ✅ List Uploaded Files - Success
- ✅ Delete File - Success
- ❌ Delete File - File Not Found

### **Project Management Tests:**
- ✅ Get All Project Names - Success
- ❌ Get Project Names - Service Exception

### **Application Tests:**
- ✅ Application Context Loads Successfully

## 🚨 Troubleshooting

### **If Allure CLI installation fails:**
```bash
# Check if you have admin rights
# Try running command prompt as administrator
```

### **If no test results exist:**
```bash
# Run tests first (even if they fail, results will be generated)
# Check build/allure-results/ for JSON files
```

### **If browser doesn't open:**
- Check console output for the URL (usually http://localhost:8080)
- Manually open the URL in your browser
- Try different browsers (Chrome, Firefox, Edge)

### **If report is empty:**
- Make sure tests have run at least once
- Check that build/allure-results/ contains JSON files
- Verify Allure annotations are properly imported in test classes

## 📞 Quick Help Commands

```bash
# Check if Allure is installed
allure --version

# Generate report from existing results
allure generate build/allure-results -o build/allure-report --clean

# Serve report (starts local server)
allure serve build/allure-results

# Open static report
start build/reports/allure-report/index.html
```

## 🎯 Expected Report URL

Once you run `allure serve`, the report will typically be available at:
- **URL**: `http://localhost:8080` (or next available port)
- **Auto-open**: Should open automatically in your default browser
- **Manual access**: Copy the URL from console output

## 📱 Report Features You'll See

1. **Overview Dashboard** - Summary statistics and charts
2. **Categories** - Tests grouped by failure types
3. **Suites** - Tests organized by Epic/Feature/Story
4. **Graphs** - Visual representation of test results
5. **Timeline** - Chronological test execution view
6. **Behaviors** - BDD-style feature organization

The report will show all our implemented test cases with rich details, step-by-step execution, and beautiful visualizations! 