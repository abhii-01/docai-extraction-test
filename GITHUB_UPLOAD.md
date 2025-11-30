# Upload to GitHub - Step-by-Step Guide

Guide to create a new GitHub repository for this Document AI test project.

## Pre-Upload Checklist

**IMPORTANT**: Before uploading, verify these files are NOT being committed:

- [ ] `credentials/*.json` (Google Cloud credentials)
- [ ] `.env` (environment variables with API keys)
- [ ] `sample_pdfs/*.pdf` (test PDFs)
- [ ] `output/*.json` (test results)

These are already in `.gitignore`, but double-check!

---

## Step 1: Create GitHub Repository

### Option A: Via GitHub Website (Recommended)

1. Go to: https://github.com/new
2. Fill in repository details:
   - **Repository name**: `docai-extraction-test`
   - **Description**: `Google Document AI testing environment for PDF text extraction with tables and flowcharts`
   - **Visibility**: 
     - ✅ **Public** (if you want to share)
     - ✅ **Private** (recommended - has credentials setup)
   - **Initialize repository**: 
     - ❌ **Do NOT add README** (we already have one)
     - ❌ **Do NOT add .gitignore** (we already have one)
     - ❌ **Do NOT choose a license** (add later if needed)
3. Click **"Create repository"**
4. **Copy the repository URL** shown (will look like: `https://github.com/abhii-01/docai-extraction-test.git`)

### Option B: Via GitHub CLI (If installed)

```bash
cd /Users/aadarsh/Documents/code/docai-test
gh repo create docai-extraction-test --private --source=. --remote=origin --push
```

---

## Step 2: Initialize Git Repository Locally

Open Terminal and run:

```bash
cd /Users/aadarsh/Documents/code/docai-test

# Initialize git
git init

# Add all files (respecting .gitignore)
git add .

# Check what will be committed (VERIFY no credentials!)
git status

# IMPORTANT: Verify these are NOT listed:
# - credentials/*.json
# - .env
# - sample_pdfs/*.pdf
# - output/*.json
```

**⚠️ STOP HERE** if you see any credentials or API keys listed!

---

## Step 3: Create Initial Commit

```bash
# Commit the code
git commit -m "Initial commit: Document AI test environment

- Complete test suite (5 tests)
- Utils for Document AI, table conversion, vision LLM
- Comprehensive documentation
- Setup instructions for Google Cloud
- Sample PDF download guide
- Cost tracking and quality assessment tools"
```

---

## Step 4: Add GitHub Remote

**Replace `YOUR_USERNAME` with your actual GitHub username:**

```bash
# Add remote (use URL from Step 1)
git remote add origin https://github.com/YOUR_USERNAME/docai-extraction-test.git

# Verify remote
git remote -v
```

**Example** (if your username is `abhii-01`):
```bash
git remote add origin https://github.com/abhii-01/docai-extraction-test.git
```

---

## Step 5: Push to GitHub

```bash
# Set main as default branch
git branch -M main

# Push to GitHub
git push -u origin main
```

**If prompted for credentials:**
- Username: Your GitHub username
- Password: Use **Personal Access Token** (not your GitHub password)

**Don't have a token?** Create one at: https://github.com/settings/tokens

---

## Step 6: Verify Upload

1. Go to: `https://github.com/YOUR_USERNAME/docai-extraction-test`
2. Check that you see:
   - ✅ README.md displays properly
   - ✅ All markdown files present
   - ✅ Python files in utils/ and tests/
   - ✅ requirements.txt
   - ❌ **NO credentials files**
   - ❌ **NO .env file**
   - ❌ **NO PDF files**

---

## Step 7: Add Repository Description (Optional)

On GitHub repository page:
1. Click **⚙️ Settings** (top right)
2. Add **Description**: 
   ```
   Google Document AI testing environment for PDF extraction with table/flowchart handling
   ```
3. Add **Topics** (tags):
   - `document-ai`
   - `pdf-extraction`
   - `google-cloud`
   - `ocr`
   - `python`
   - `llm`

---

## Step 8: Create README Badge (Optional)

Add this to the top of README.md:

```markdown
# Google Document AI Test Extraction

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Document%20AI-blue.svg)
```

Then commit and push:
```bash
git add README.md
git commit -m "Add badges to README"
git push
```

---

## Future Updates

When you make changes:

```bash
cd /Users/aadarsh/Documents/code/docai-test

# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push
```

---

## Common Issues

### Issue: "Permission denied"

**Solution**: Set up SSH key or use Personal Access Token

**Quick fix**: Use token authentication
```bash
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/docai-extraction-test.git
```

### Issue: ".env file is being tracked"

**Solution**: Remove from git
```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
git push
```

### Issue: "Large PDF files rejected"

**Solution**: They should already be gitignored, but if not:
```bash
git rm --cached sample_pdfs/*.pdf
git commit -m "Remove PDF files from tracking"
git push
```

---

## Clone on Another Machine

To work on this project elsewhere:

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/docai-extraction-test.git
cd docai-extraction-test

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env from template
cp env_template.txt .env
nano .env  # Add your credentials

# Add credentials JSON
cp /path/to/your/credentials.json credentials/docai-credentials.json

# Download sample PDFs
./download_samples.sh

# Run tests
python tests/test1_basic_extraction.py --verify-setup
```

---

## Security Checklist ✅

Before pushing, always verify:

- [ ] No API keys in code
- [ ] No credentials JSON files
- [ ] No .env file
- [ ] .gitignore is working
- [ ] All secrets in env_template.txt are placeholders
- [ ] README doesn't contain actual credentials

---

## Git Commands Quick Reference

```bash
# Check status
git status

# See what changed
git diff

# View commit history
git log --oneline

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Pull latest changes
git pull

# Push to GitHub
git push
```

---

## Recommended .gitignore Additions

Already included in `.gitignore`, but verify:

```
# Credentials
credentials/*.json
.env

# Test files
sample_pdfs/*.pdf
output/*.json
output/*.txt
output/*.png

# Python
venv/
__pycache__/
*.pyc

# OS
.DS_Store
```

---

## Complete Upload Commands (Copy-Paste)

**Replace `YOUR_USERNAME` with your GitHub username:**

```bash
# Navigate to project
cd /Users/aadarsh/Documents/code/docai-test

# Initialize git
git init

# Add all files
git add .

# Verify no credentials (IMPORTANT!)
git status

# Create initial commit
git commit -m "Initial commit: Document AI test environment"

# Add GitHub remote (REPLACE YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/docai-extraction-test.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

**Ready to upload?** Run the commands in Step 2-5!

**Repository will be at**: `https://github.com/YOUR_USERNAME/docai-extraction-test`

