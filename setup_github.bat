@echo off
echo ====================================
echo MT5-TradeBot API - GitHub Setup
echo ====================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/6] Initializing Git repository...
git init
if errorlevel 1 (
    echo ERROR: Failed to initialize Git repository
    pause
    exit /b 1
)
echo ✓ Git repository initialized

echo.
echo [2/6] Renaming main README for GitHub...
if exist GITHUB_README.md (
    if exist README.md (
        move README.md README_OLD.md
        echo ✓ Old README backed up to README_OLD.md
    )
    move GITHUB_README.md README.md
    echo ✓ GitHub README is now main README.md
)

echo.
echo [3/6] Adding all files to Git...
git add .
if errorlevel 1 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)
echo ✓ All files added

echo.
echo [4/6] Creating initial commit...
git commit -m "Initial commit: MT5-TradeBot API v1.0 - Professional MetaTrader 5 API"
if errorlevel 1 (
    echo ERROR: Failed to create commit
    pause
    exit /b 1
)
echo ✓ Initial commit created

echo.
echo [5/6] Renaming branch to 'main'...
git branch -M main
echo ✓ Branch renamed to main

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Next Steps:
echo.
echo 1. Create a new repository on GitHub:
echo    - Go to: https://github.com/new
echo    - Name: mt5-tradebot-api
echo    - Description: Professional RESTful API for MetaTrader 5 Expert Advisor Testing
echo    - Make it Public or Private
echo    - DO NOT initialize with README
echo.
echo 2. Copy your repository URL (it will look like):
echo    https://github.com/YOUR_USERNAME/mt5-tradebot-api.git
echo.
echo 3. Run this command with YOUR repository URL:
echo    git remote add origin https://github.com/YOUR_USERNAME/mt5-tradebot-api.git
echo    git push -u origin main
echo.
echo OR run: push_to_github.bat (after creating the repository)
echo.
pause
