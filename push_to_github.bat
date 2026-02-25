@echo off
echo ====================================
echo Push to GitHub
echo ====================================
echo.

REM Prompt for GitHub username
set /p GITHUB_USER="Enter your GitHub username: "
if "%GITHUB_USER%"=="" (
    echo ERROR: Username cannot be empty
    pause
    exit /b 1
)

REM Prompt for repository name (with default)
set /p REPO_NAME="Enter repository name (default: mt5-tradebot-api): "
if "%REPO_NAME%"=="" set REPO_NAME=mt5-tradebot-api

echo.
echo Repository URL will be:
echo https://github.com/%GITHUB_USER%/%REPO_NAME%.git
echo.
set /p CONFIRM="Is this correct? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Cancelled by user
    pause
    exit /b 0
)

echo.
echo [1/2] Adding remote origin...
git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
if errorlevel 1 (
    echo.
    echo Remote 'origin' might already exist. Updating...
    git remote set-url origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
)
echo ✓ Remote configured

echo.
echo [2/2] Pushing to GitHub...
echo.
echo NOTE: You may be prompted for your GitHub credentials
echo If using 2FA, you'll need a Personal Access Token instead of password
echo.
git push -u origin main
if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Common issues:
    echo 1. Repository doesn't exist on GitHub - create it first at https://github.com/new
    echo 2. Authentication failed - check your credentials
    echo 3. Using 2FA - you need a Personal Access Token from:
    echo    https://github.com/settings/tokens
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================
echo Success!
echo ====================================
echo.
echo Your repository is now on GitHub at:
echo https://github.com/%GITHUB_USER%/%REPO_NAME%
echo.
echo View it in your browser? (Opening...)
start https://github.com/%GITHUB_USER%/%REPO_NAME%
echo.
pause
