# 🤖 Automated GitHub Setup Guide

This guide will help you automatically set up and deploy your MT5-TradeBot API to GitHub.

## 🎯 What This Automation Does

- ✅ Initializes Git repository
- ✅ Renames files for GitHub
- ✅ Creates initial commit
- ✅ Sets up GitHub Actions (CI/CD)
- ✅ Configures automated testing
- ✅ Pushes to GitHub automatically

---

## 📋 Prerequisites

### 1. Install Git

**Check if Git is installed:**
```bash
git --version
```

**If not installed:**
- Download from: https://git-scm.com/download/win
- Run installer with default settings
- Restart Command Prompt

### 2. Create GitHub Account

- Go to: https://github.com/signup
- Create free account
- Verify your email

### 3. (Optional) Set up Git credentials

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🚀 Method 1: Fully Automated (Recommended)

### Step 1: Run Setup Script

Double-click: **`setup_github.bat`**

This will:
- Initialize Git
- Rename README files
- Create initial commit
- Prepare for GitHub

### Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name:** `mt5-tradebot-api`
   - **Description:** `Professional RESTful API for MetaTrader 5 Expert Advisor Testing`
   - **Visibility:** Public (recommended) or Private
   - **DO NOT** check "Initialize with README"
3. Click **"Create repository"**

### Step 3: Push to GitHub

Double-click: **`push_to_github.bat`**

Follow the prompts:
1. Enter your GitHub username
2. Confirm repository name
3. Enter credentials when prompted

**Done!** Your project is now on GitHub! 🎉

---

## 🔧 Method 2: Manual Commands

If you prefer command line:

### Step 1: Initialize Repository

```bash
# Navigate to project folder
cd c:\Users\zenox\Desktop\llmfit-v0.4.5-x86_64-pc-windows-msvc

# Initialize Git
git init

# Rename README
move GITHUB_README.md README.md

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: MT5-TradeBot API v1.0"

# Rename branch to main
git branch -M main
```

### Step 2: Create GitHub Repository

Go to https://github.com/new and create repository (see Method 1, Step 2)

### Step 3: Push to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/mt5-tradebot-api.git
git push -u origin main
```

---

## 🔐 Authentication Options

### Option A: HTTPS with Personal Access Token (Recommended)

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `MT5-TradeBot-API`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click **"Generate token"**
6. **COPY THE TOKEN** (you won't see it again!)
7. When pushing, use token as password:
   - Username: `your_github_username`
   - Password: `paste_your_token_here`

### Option B: SSH Keys (Advanced)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Copy public key
type %USERPROFILE%\.ssh\id_ed25519.pub

# Add to GitHub:
# Go to: https://github.com/settings/keys
# Click "New SSH key"
# Paste the key

# Use SSH URL instead:
git remote add origin git@github.com:YOUR_USERNAME/mt5-tradebot-api.git
```

---

## 🤖 GitHub Actions (Automated Testing)

Your repository includes automated workflows:

### 1. Python API Tests (`.github/workflows/python-test.yml`)

**Runs on:** Every push and pull request

**Tests:**
- Python 3.8, 3.9, 3.10, 3.11 compatibility
- Dependency installation
- Code linting
- Import checks

**View results:**
- Go to your repository
- Click **"Actions"** tab
- See test results

### 2. Documentation Check (`.github/workflows/documentation.yml`)

**Runs on:** Every push and pull request

**Checks:**
- All documentation files exist
- No broken links
- Markdown formatting

### How to Enable GitHub Actions

1. Push your code to GitHub
2. Go to repository → **"Actions"** tab
3. Click **"I understand my workflows, go ahead and enable them"**
4. Actions will run automatically on next push!

---

## 📝 Making Updates

### After Initial Setup

Whenever you make changes:

```bash
# Check what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Add: description of what you changed"

# Push to GitHub
git push
```

### Quick Update Script

Create `update_github.bat`:
```batch
@echo off
git add .
set /p MESSAGE="Commit message: "
git commit -m "%MESSAGE%"
git push
echo Done!
pause
```

---

## 🎨 Customizing Your Repository

### Add Repository Topics

1. Go to your repository on GitHub
2. Click ⚙️ next to "About"
3. Add topics:
   - `metatrader5`
   - `trading-bot`
   - `forex`
   - `api`
   - `python`
   - `fastapi`
   - `backtesting`

### Add Social Preview Image

1. Create a 1280x640 image with your project name
2. Go to repository → Settings → Options
3. Scroll to "Social preview"
4. Upload image

### Enable Discussions

1. Go to Settings → Features
2. Check ✅ "Discussions"
3. Community can now ask questions!

---

## 🔍 Troubleshooting

### "Git is not recognized"

**Solution:** Install Git and restart Command Prompt
- Download: https://git-scm.com/download/win

### "Permission denied (publickey)"

**Solution:** Use HTTPS instead of SSH, or set up SSH keys properly

### "Repository not found"

**Solution:** 
1. Check repository exists on GitHub
2. Verify username and repository name are correct
3. Check you have access to the repository

### "Authentication failed"

**Solution:**
1. If using 2FA, you MUST use Personal Access Token
2. Generate token at: https://github.com/settings/tokens
3. Use token as password

### "Remote origin already exists"

**Solution:**
```bash
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/mt5-tradebot-api.git
```

### "Nothing to commit"

**Solution:** You haven't made any changes
```bash
# Check status
git status

# Make some changes, then:
git add .
git commit -m "Your message"
```

---

## 📊 Repository Statistics

After setup, you can add badges to your README:

### GitHub Stats Badges

```markdown
![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/mt5-tradebot-api)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/mt5-tradebot-api)
![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/mt5-tradebot-api)
![GitHub license](https://img.shields.io/github/license/YOUR_USERNAME/mt5-tradebot-api)
```

### Build Status Badge

```markdown
![Tests](https://github.com/YOUR_USERNAME/mt5-tradebot-api/workflows/Python%20API%20Tests/badge.svg)
```

---

## 🌟 Best Practices

### Commit Messages

**Good:**
- `Add: backtesting feature for RSI strategy`
- `Fix: connection timeout issue with MT5`
- `Update: documentation for beginners`
- `Remove: deprecated API endpoint`

**Bad:**
- `update`
- `fix bug`
- `changes`

### Branching Strategy

```bash
# Create feature branch
git checkout -b feature/new-strategy

# Make changes and commit
git add .
git commit -m "Add: MACD crossover strategy"

# Push feature branch
git push -u origin feature/new-strategy

# Create Pull Request on GitHub
# After merge, switch back to main
git checkout main
git pull
```

### .gitignore Best Practices

Already included in your `.gitignore`:
- `.env` (credentials)
- `__pycache__/` (Python cache)
- `*.pyc` (compiled Python)
- `.vscode/` (editor settings)

**Never commit:**
- Passwords
- API keys
- Personal data
- Large binary files

---

## 📚 Additional Resources

### GitHub Learning

- GitHub Docs: https://docs.github.com
- Git Handbook: https://guides.github.com/introduction/git-handbook/
- GitHub Skills: https://skills.github.com

### Git Commands Cheat Sheet

```bash
# Status
git status                    # Check what changed
git log                       # View commit history
git diff                      # See changes

# Branching
git branch                    # List branches
git branch feature-name       # Create branch
git checkout feature-name     # Switch branch
git checkout -b feature-name  # Create and switch

# Undoing
git reset HEAD file.py        # Unstage file
git checkout -- file.py       # Discard changes
git revert commit-hash        # Undo commit

# Remote
git remote -v                 # List remotes
git fetch                     # Download changes
git pull                      # Download and merge
git push                      # Upload changes
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Repository visible on GitHub
- [ ] README displays correctly
- [ ] All files uploaded
- [ ] GitHub Actions enabled
- [ ] Tests passing (green checkmark)
- [ ] License file present
- [ ] Topics added
- [ ] Description set

---

## 🆘 Getting Help

**If automation fails:**

1. Check error messages carefully
2. Verify Git is installed: `git --version`
3. Ensure GitHub repository exists
4. Check credentials are correct
5. Try manual method instead

**Need more help?**

- Open an issue on GitHub
- Check GitHub Community: https://github.community
- Git documentation: https://git-scm.com/doc

---

## 🎉 Success!

Once your repository is on GitHub:

1. **Share it:** Send link to friends/colleagues
2. **Star it:** Give yourself a star! ⭐
3. **Watch it:** Get notifications for issues
4. **Contribute:** Keep improving it
5. **Promote it:** Share on social media

**Your repository URL:**
```
https://github.com/YOUR_USERNAME/mt5-tradebot-api
```

---

**Happy coding! 🚀**

Remember: Open source is about sharing and learning together!
