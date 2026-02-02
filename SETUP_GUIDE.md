# 🚀 Complete Setup Guide

This guide will walk you through setting up the Kids Educational Content Automation system from scratch.

---

## Part 1: Prerequisites

### 1.1 Install Python

**Check if Python is installed:**
```bash
python --version
# or
python3 --version
```

You need Python 3.8 or higher.

**Install Python:**
- **Ubuntu/Debian**: `sudo apt-get install python3 python3-pip python3-venv`
- **macOS**: `brew install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### 1.2 Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

**Verify installation:**
```bash
ffmpeg -version
```

---

## Part 2: Get API Keys

### 2.1 Longcat AI API Key

1. Visit [https://longcat.chat/platform/](https://longcat.chat/platform/)
2. Click "Register" or "Sign In"
3. Complete registration
4. Navigate to "API Keys" page
5. Click "Create API Key"
6. Copy your API key (starts with `sk-...`)
7. Save it securely - you'll need it later

**Free Quota:**
- Default: 500,000 tokens/day
- Can request increase to 5,000,000 tokens/day

### 2.2 YouTube API Credentials

#### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click "Select a project" > "New Project"
4. Enter project name: "Kids Educational Content"
5. Click "Create"

#### Step 2: Enable YouTube Data API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "YouTube Data API v3"
3. Click on it
4. Click "Enable"

#### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Click "Create"
4. Fill in required fields:
   - **App name**: Kids Educational Content
   - **User support email**: Your email
   - **Developer contact**: Your email
5. Click "Save and Continue"
6. On "Scopes" page, click "Add or Remove Scopes"
7. Search for "YouTube Data API v3"
8. Select: `https://www.googleapis.com/auth/youtube.upload`
9. Click "Update" > "Save and Continue"
10. On "Test users" page, add your Google account email
11. Click "Save and Continue"
12. Review and click "Back to Dashboard"

#### Step 4: Create OAuth Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app"
4. Name: "Kids Edu Desktop Client"
5. Click "Create"
6. Click "Download JSON"
7. Save the file

---

## Part 3: Project Setup

### 3.1 Download/Clone Project

**Option A: Clone from Git**
```bash
git clone <your-repo-url>
cd kids-edu-shorts
```

**Option B: Download ZIP**
1. Download and extract the ZIP file
2. Open terminal/command prompt
3. Navigate to the extracted folder:
   ```bash
   cd path/to/kids-edu-shorts
   ```

### 3.2 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 3.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take a few minutes.

### 3.4 Create Required Directories

```bash
mkdir -p temp_assets logs
```

---

## Part 4: Configuration

### 4.1 Setup Environment Variables

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file:
   ```bash
   nano .env  # or use any text editor
   ```

3. Replace with your values:
   ```bash
   LONGCAT_API_KEY=sk-your-actual-api-key-here
   LONGCAT_BASE_URL=https://api.longcat.chat/openai
   MALE_VOICE=en-US-GuyNeural
   POST_TIMES=08:00,20:00
   TIMEZONE=UTC
   ```

4. Save and close

### 4.2 Setup YouTube Credentials

1. Take the JSON file you downloaded from Google Cloud Console
2. Rename it to `client_secrets.json`
3. Move it to the project root directory:
   ```bash
   mv ~/Downloads/client_secret_*.json ./client_secrets.json
   ```

---

## Part 5: First Run & Authentication

### 5.1 Test the Application

Run the application once to complete YouTube authentication:

```bash
python main.py --mode once
```

### 5.2 Complete OAuth Flow

1. A browser window will open automatically
2. Sign in with your Google account (the one you added as test user)
3. You'll see a warning "Google hasn't verified this app"
   - Click "Advanced"
   - Click "Go to Kids Educational Content (unsafe)"
4. Review permissions
5. Click "Continue"
6. You'll see "The authentication flow has completed"
7. Close the browser window

### 5.3 Verify Authentication

Check that `youtube_token.pickle` was created:
```bash
ls -la youtube_token.pickle
```

If you see the file, authentication was successful!

---

## Part 6: Test Video Creation

### 6.1 Generate Test Topics

The first run will automatically generate 200 topics. This takes about 1-2 minutes.

### 6.2 Monitor Progress

Watch the logs in real-time:
```bash
tail -f logs/app.log
```

You should see:
1. "Generating topics..."
2. "Generating lesson content..."
3. "Creating video..."
4. "Uploading to YouTube..."
5. "Video uploaded successfully!"

### 6.3 Check Your YouTube Channel

1. Go to [YouTube Studio](https://studio.youtube.com/)
2. Click "Content"
3. You should see your newly uploaded Short!

---

## Part 7: Deployment

### Option A: Run Locally with Scheduling

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run in scheduled mode (2 posts per day)
python main.py --mode scheduled
```

Keep the terminal window open. The app will post at scheduled times.

**To run in background (Linux/Mac):**
```bash
nohup python main.py --mode scheduled > output.log 2>&1 &
```

### Option B: Deploy with GitHub Actions

#### Step 1: Create GitHub Repository

1. Create a new repository on GitHub
2. Initialize git in your project:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

#### Step 2: Add GitHub Secrets

1. Go to your repository on GitHub
2. Click "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add these secrets:

**Secret 1: LONGCAT_API_KEY**
- Name: `LONGCAT_API_KEY`
- Value: Your Longcat API key

**Secret 2: YOUTUBE_CLIENT_SECRETS**
- Name: `YOUTUBE_CLIENT_SECRETS`
- Value: Contents of `client_secrets.json` file
  ```bash
  cat client_secrets.json
  ```
  Copy the entire JSON output

#### Step 3: Prepare YouTube Token

```bash
# Encode token to base64
base64 youtube_token.pickle > youtube_token.pickle.b64

# Add to git
git add youtube_token.pickle.b64
git commit -m "Add YouTube token"
git push
```

#### Step 4: Enable GitHub Actions

1. Go to "Actions" tab in your repository
2. Click "I understand my workflows, go ahead and enable them"
3. The workflow will run automatically at scheduled times

#### Step 5: Test Manual Run

1. Go to "Actions" tab
2. Click "Kids Educational Content - Daily Posts"
3. Click "Run workflow"
4. Select branch: main
5. Click "Run workflow"
6. Watch the progress

---

## Part 8: Verification

### 8.1 Check Database

```bash
sqlite3 app_data.db "SELECT COUNT(*) FROM topics;"
# Should show 200

sqlite3 app_data.db "SELECT COUNT(*) FROM topics WHERE status='unused';"
# Should show 199 (one used)

sqlite3 app_data.db "SELECT * FROM upload_history;"
# Should show your upload
```

### 8.2 Check Logs

```bash
tail -n 50 logs/app.log
```

Look for:
- ✅ "Video uploaded successfully"
- ✅ "Shorts URL: https://www.youtube.com/shorts/..."
- ❌ No ERROR messages

### 8.3 Check YouTube

1. Go to [YouTube Studio](https://studio.youtube.com/)
2. Check video details:
   - Format: Vertical (9:16)
   - Duration: < 60 seconds
   - Category: Education
   - Made for Kids: Yes
   - Title includes "#Shorts"

---

## Part 9: Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "FFmpeg not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

### Issue: "YouTube authentication failed"

**Solution:**
1. Delete token file:
   ```bash
   rm youtube_token.pickle
   ```
2. Run again:
   ```bash
   python main.py --mode once
   ```
3. Complete OAuth flow in browser

### Issue: "Longcat API error"

**Solution:**
1. Check API key in `.env`:
   ```bash
   cat .env | grep LONGCAT_API_KEY
   ```
2. Verify key is active at [https://longcat.chat/platform/](https://longcat.chat/platform/)
3. Check quota usage

### Issue: "Video too long (>60s)"

**Solution:**
Edit `video_producer.py`, line 50:
```python
# Change from:
communicate = edge_tts.Communicate(text, self.male_voice, rate="-10%")

# To:
communicate = edge_tts.Communicate(text, self.male_voice, rate="+10%")
```

This speeds up the voice slightly.

---

## Part 10: Maintenance

### Daily Checks

```bash
# Check logs
tail -f logs/app.log

# Check unused topics
sqlite3 app_data.db "SELECT COUNT(*) FROM topics WHERE status='unused';"

# Check recent uploads
sqlite3 app_data.db "SELECT * FROM upload_history ORDER BY uploaded_at DESC LIMIT 5;"
```

### Weekly Tasks

1. **Review uploaded videos**:
   - Check quality
   - Monitor views and engagement
   - Adjust content if needed

2. **Clean old logs**:
   ```bash
   find logs/ -name "*.log" -mtime +30 -delete
   ```

3. **Backup database**:
   ```bash
   cp app_data.db backups/app_data_$(date +%Y%m%d).db
   ```

### Monthly Tasks

1. **Update dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Review topic categories**:
   - Add new categories if needed
   - Regenerate topics

3. **Check API quotas**:
   - Longcat AI usage
   - YouTube API quota

---

## 🎉 Congratulations!

You've successfully set up the Kids Educational Content Automation system!

### Next Steps:

1. **Monitor first few posts** to ensure quality
2. **Adjust scheduling** if needed (edit `POST_TIMES` in `.env`)
3. **Customize content** (edit categories in `topic_manager.py`)
4. **Add more features** (see README.md for ideas)

### Need Help?

- Check `README.md` for detailed documentation
- Review logs in `logs/app.log`
- Check [Longcat AI docs](https://longcat.chat/platform/docs/)
- Check [YouTube API docs](https://developers.google.com/youtube/v3)

**Happy automating! 🚀**
