@echo off
echo ========================================
echo    Zenius AI - Allure Report Viewer
echo ========================================
echo.

echo Step 1: Running tests to generate Allure results...
echo.
gradlew.bat clean test
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Tests failed! Check the output above.
    echo You can still generate a report from existing results if any.
    echo.
    pause
)

echo.
echo Step 2: Generating Allure HTML report...
echo.
gradlew.bat allureReport
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to generate Allure report!
    echo Make sure Allure CLI is installed.
    echo.
    echo To install Allure:
    echo - Using Chocolatey: choco install allure
    echo - Using npm: npm install -g allure-commandline
    echo.
    pause
    exit /b 1
)

echo.
echo Step 3: Opening Allure report in browser...
echo.
echo The report will open in your default browser.
echo If it doesn't open automatically, you can access it at:
echo http://localhost:8080 (or the port shown below)
echo.

gradlew.bat serveAllureReport

echo.
echo Report viewing session ended.
pause 