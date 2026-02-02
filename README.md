# 🎓 Kids Educational Content Automation for YouTube Shorts

An automated Python application that generates halal, kid-friendly educational content, creates high-quality vertical videos (9:16), and posts them to YouTube Shorts twice daily.

## ✨ Features

### Content Generation
- **AI-Powered Topics**: Generates 200 unique, kid-friendly topics per batch using Longcat AI
- **Halal & Safe Content**: All content is carefully designed to be appropriate, educational, and safe for children
- **20 Educational Categories**: Covers Good Manners, Math Basics, English, Islamic Manners, and more
- **Smart Topic Management**: Automatically recycles topics with new content when exhausted

### Video Production
- **Professional Quality**: 1080x1920 vertical videos optimized for YouTube Shorts
- **Male Voice Narration**: Natural, calm male voice using Edge-TTS (free)
- **4-Slide Structure**: Title, Explanation, Examples, Practice/Reflection
- **Safe Design**: Large margins, no text clipping, high contrast for readability
- **Content Restrictions**: No humans, faces, or animals - only text, shapes, and patterns

### Automation
- **YouTube Shorts Integration**: Automatic upload with proper metadata and tags
- **Scheduled Posting**: 2 videos per day at customizable times
- **Error Recovery**: Robust retry logic and continuous operation
- **Automatic Cleanup**: Removes temporary files after successful upload
- **GitHub Actions Support**: Deploy and run entirely in the cloud

---

## 📋 Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [YouTube API Setup](#youtube-api-setup)
5. [Usage](#usage)
6. [Deployment Options](#deployment-options)
7. [Project Structure](#project-structure)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## 🔧 Requirements

### System Requirements
- Python 3.8 or higher
- FFmpeg (for video processing)
- Internet connection

### API Requirements
- **Longcat AI API Key** (for content generation)
  - Sign up at [https://longcat.chat/platform/](https://longcat.chat/platform/)
  - Free tier: 500,000 tokens/day (can be increased to 5M)
  
- **YouTube Data API v3** (for video uploads)
  - OAuth 2.0 credentials from Google Cloud Console
  - See [YouTube API Setup](#youtube-api-setup) section

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd kids-edu-shorts
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg

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
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

### 5. Create Required Directories

```bash
mkdir -p temp_assets logs
```

---

## ⚙️ Configuration

### 1. Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Longcat AI Configuration
LONGCAT_API_KEY=your_longcat_api_key_here
LONGCAT_BASE_URL=https://api.longcat.chat/openai

# Voice Configuration
MALE_VOICE=en-US-GuyNeural

# Scheduling Configuration
POST_TIMES=08:00,20:00
TIMEZONE=UTC
```

### 2. Available Male Voices (Edge-TTS)

- `en-US-GuyNeural` (American English) - Default
- `en-GB-RyanNeural` (British English)
- `en-AU-WilliamNeural` (Australian English)
- `en-CA-LiamNeural` (Canadian English)

---

## 🎬 YouTube API Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **YouTube Data API v3**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure OAuth consent screen:
   - User Type: External
   - App name: Kids Educational Content
   - Add your email
   - Add scope: `https://www.googleapis.com/auth/youtube.upload`
4. Create OAuth client ID:
   - Application type: Desktop app
   - Name: Kids Edu Automation
5. Download the JSON file
6. Rename it to `client_secrets.json` and place in project root

### Step 3: First-Time Authentication

Run the application once locally to complete OAuth flow:

```bash
python main.py --mode once
```

This will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request permission to upload videos
4. Save authentication token to `youtube_token.pickle`

**Important**: Keep `youtube_token.pickle` secure - it allows uploading videos to your channel!

---

## 🚀 Usage

### Run Once (Single Video)

```bash
python main.py --mode once
```

### Run Scheduled (2 Posts Per Day)

```bash
python main.py --mode scheduled
```

This will post at times specified in `.env` (default: 08:00 and 20:00).

### Run Continuous (Custom Interval)

```bash
python main.py --mode continuous --interval 12
```

This will post every 12 hours (or your specified interval).

### Command-Line Options

```bash
python main.py --help
```

Options:
- `--mode`: Execution mode (`once`, `scheduled`, `continuous`)
- `--interval`: Hours between posts in continuous mode (default: 12)

---

## 🌐 Deployment Options

### Option 1: GitHub Actions (Recommended)

**Advantages:**
- Free for public repositories
- No server maintenance
- Automatic scheduling
- Version control integration

**Setup:**

1. Push code to GitHub
2. Add repository secrets:
   - `LONGCAT_API_KEY`: Your Longcat API key
   - `YOUTUBE_CLIENT_SECRETS`: Contents of `client_secrets.json` file
3. Complete first-time authentication locally
4. Commit `youtube_token.pickle.b64` to repository:
   ```bash
   base64 youtube_token.pickle > youtube_token.pickle.b64
   git add youtube_token.pickle.b64
   git commit -m "Add YouTube token"
   git push
   ```

The workflow will run automatically at scheduled times (08:00 and 20:00 UTC).

### Option 2: Local/Server Deployment

**Using systemd (Linux):**

Create service file `/etc/systemd/system/kids-edu.service`:

```ini
[Unit]
Description=Kids Educational Content Automation
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/kids-edu-shorts
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python main.py --mode scheduled
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable kids-edu
sudo systemctl start kids-edu
sudo systemctl status kids-edu
```

**Using cron:**

```bash
crontab -e
```

Add:
```
0 8,20 * * * cd /path/to/kids-edu-shorts && /path/to/venv/bin/python main.py --mode once
```

### Option 3: Cloud VPS (DigitalOcean, AWS, etc.)

1. Deploy code to VPS
2. Set up systemd service (see above)
3. Configure firewall if needed
4. Set up monitoring/alerts

---

## 📁 Project Structure

```
kids-edu-shorts/
├── main.py                    # Main orchestrator
├── db_manager.py              # Database operations
├── topic_manager.py           # Topic generation
├── content_generator.py       # Lesson content creation
├── video_producer.py          # Video creation
├── youtube_publisher.py       # YouTube upload
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── client_secrets.json       # YouTube OAuth credentials (not in git)
├── youtube_token.pickle      # YouTube auth token (not in git)
├── app_data.db              # SQLite database (auto-created)
├── temp_assets/             # Temporary video files (auto-cleaned)
├── logs/                    # Application logs
└── .github/
    └── workflows/
        └── daily_post.yml   # GitHub Actions workflow
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "No module named 'moviepy'"**
```bash
pip install -r requirements.txt
```

**2. "FFmpeg not found"**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

**3. "YouTube authentication failed"**
- Ensure `client_secrets.json` is in project root
- Delete `youtube_token.pickle` and re-authenticate
- Check OAuth consent screen is configured correctly

**4. "Longcat API key invalid"**
- Verify API key in `.env` file
- Check API key is active at [https://longcat.chat/platform/](https://longcat.chat/platform/)

**5. "Video duration exceeds 60 seconds"**
- Lesson content is too long
- Adjust voice speed in `video_producer.py` (increase rate parameter)
- Simplify lesson content

**6. "Upload quota exceeded"**
- YouTube has daily upload limits
- Wait 24 hours or request quota increase from Google

### Logs

Check logs for detailed error information:
```bash
tail -f logs/app.log
```

---

## ❓ FAQ

### Q: How much does it cost to run?

**A:** 
- Longcat AI: Free (500K-5M tokens/day)
- Edge-TTS: Free
- YouTube API: Free (with daily limits)
- GitHub Actions: Free for public repos
- Total: **$0/month** for basic usage

### Q: Can I change the video format?

**A:** Yes, edit `video_producer.py`:
- Change `self.width` and `self.height` for different aspect ratios
- Modify colors in `self.bg_color`, `self.text_color`, `self.accent_color`

### Q: Can I add background music?

**A:** Yes, but ensure:
- Music is royalty-free or you have rights
- Volume is lower than voice
- Add in `video_producer.py` using moviepy's `CompositeAudioClip`

### Q: How do I add more categories?

**A:** Edit `topic_manager.py`:
- Add categories to `self.categories` list
- Regenerate topics

### Q: Can I post to other platforms?

**A:** Yes, you can extend the code:
- TikTok: Use unofficial API or browser automation
- Instagram Reels: Requires Facebook Graph API
- Twitter/X: Use Twitter API

### Q: What if I want female voice?

**A:** Change in `.env`:
```bash
MALE_VOICE=en-US-JennyNeural  # Female voice
```

But note: User requirements specified male voice only.

### Q: How do I backup my data?

**A:**
```bash
# Backup database
cp app_data.db app_data.db.backup

# Backup authentication
cp youtube_token.pickle youtube_token.pickle.backup
```

---

## 🔐 Security Best Practices

1. **Never commit secrets to Git**:
   - `.env` is in `.gitignore`
   - `client_secrets.json` is in `.gitignore`
   - Use GitHub Secrets for CI/CD

2. **Protect authentication tokens**:
   - Keep `youtube_token.pickle` secure
   - Rotate tokens periodically

3. **Use environment variables**:
   - Never hardcode API keys
   - Use `.env` for local development
   - Use secrets for production

4. **Regular updates**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## 📊 Monitoring

### Check Application Status

```bash
# View recent logs
tail -n 100 logs/app.log

# Check database status
sqlite3 app_data.db "SELECT COUNT(*) FROM topics WHERE status='unused';"

# View upload history
sqlite3 app_data.db "SELECT * FROM upload_history ORDER BY uploaded_at DESC LIMIT 10;"
```

### Performance Metrics

- **Topic Generation**: ~30-60 seconds for 200 topics
- **Lesson Generation**: ~5-10 seconds per lesson
- **Video Creation**: ~20-40 seconds per video
- **Upload Time**: ~10-30 seconds (depends on internet speed)
- **Total Time**: ~1-2 minutes per video

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is provided as-is for educational purposes.

---

## 🙏 Acknowledgments

- **Longcat AI** for content generation
- **Edge-TTS** for free text-to-speech
- **MoviePy** for video processing
- **YouTube Data API** for upload functionality

---

## 📞 Support

For issues and questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs in `logs/app.log`
3. Open an issue on GitHub
4. Check Longcat AI documentation: [https://longcat.chat/platform/docs/](https://longcat.chat/platform/docs/)
5. Check YouTube API documentation: [https://developers.google.com/youtube/v3](https://developers.google.com/youtube/v3)

---

## 🎯 Roadmap

Future enhancements:
- [ ] Multi-language support (Arabic, French, Spanish)
- [ ] Web dashboard for monitoring
- [ ] Custom background patterns/colors per category
- [ ] Analytics and performance tracking
- [ ] Support for longer videos (regular YouTube)
- [ ] Interactive quiz slides
- [ ] Parent/teacher feedback system

---

**Made with ❤️ for kids' education**
