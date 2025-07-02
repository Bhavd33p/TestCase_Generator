@echo off
echo Starting Test Execution for Zenius AI Test Case Generator
echo.

echo Compiling Java files...
javac -cp "src/main/java;src/test/java" src/main/java/com/zinnia/zenius/controller/DataProcessingController.java
if %errorlevel% neq 0 (
    echo Compilation failed!
    pause
    exit /b 1
)

echo.
echo Compilation successful!
echo.

echo To run the full test suite with Allure reporting:
echo 1. Fix the Gradle wrapper by running: gradlew wrapper --gradle-version 8.11.1
echo 2. Then run: gradlew clean test allureReport
echo.

echo Current implementation includes:
echo - File upload and viewing endpoints
echo - Chrome browser integration
echo - Comprehensive Allure test reporting
echo - File management functionality
echo.

echo Check the following files for the new features:
echo - DataProcessingController.java (new file viewing endpoints)
echo - DataProcessingControllerTest.java (Allure test cases)
echo - TestCaseForm.jsx (enhanced file viewing)
echo - FileManager.jsx (new file management component)
echo - application.properties (file upload configuration)
echo.

pause 