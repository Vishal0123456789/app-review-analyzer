# Groww App Review Insights Analyzer

A sophisticated 4-layer architecture system that analyzes Google Play Store reviews for the Groww app, generates actionable insights, and sends professional HTML email reports with automated scheduling.

## Overview

**Groww App Review Insights Analyzer** automatically scrapes user reviews, classifies them into key themes, generates weekly insights, and delivers comprehensive analysis reports. It supports both manual frontend-triggered analysis and automatic scheduled execution.

### Key Features

- **Smart Review Scraping**: Automatically fetches Google Play Store reviews for the Groww app
- **AI-Powered Classification**: Uses Google Gemini LLM to categorize reviews into 5 key themes
- **Insight Generation**: MAP-REDUCE pipeline for aggregate analysis and action recommendations
- **Professional Email Reports**: Beautiful HTML-formatted emails with Key Insights Dashboard, colored cards, and action roadmap
- **Dual-Mode Orchestration**: Manual UI triggering + automatic weekly scheduler (Monday 8 AM)
- **Real-Time Frontend**: React TypeScript UI with dark theme and live progress tracking
- **RESTful API**: FastAPI backend with comprehensive endpoints

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Groww App Review Analyzer               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Layer 1: Review Scraping                                    │
│  └─> Fetches reviews from Google Play Store (google-play-   │
│      scraper library) for date range analysis               │
│                                                               │
│  Layer 2: AI Classification                                  │
│  └─> Classifies reviews into 5 themes using Gemini LLM:    │
│      • Execution & Performance                              │
│      • UI & Feature Gaps                                    │
│      • Charges & Transparency                               │
│      • [Additional themes based on content]                 │
│                                                               │
│  Layer 3: Insight Generation                                 │
│  └─> MAP-REDUCE pipeline for:                               │
│      • Theme summarization                                  │
│      • User quote extraction                                │
│      • Action item generation                               │
│                                                               │
│  Layer 4: Email Delivery                                     │
│  └─> Generates beautiful HTML reports and sends via SMTP    │
│      • Header: "Weekly Product Pulse"                       │
│      • Key Insights Dashboard with colored cards            │
│      • Detailed theme analysis                              │
│      • Action roadmap with timelines                        │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Orchestration & Scheduling                                 │
│                                                               │
│  Manual Trigger (Frontend)          Auto Scheduler           │
│  └─> User clicks "Analyze"          └─> Monday 8:00 AM UTC  │
│      └─> POST /api/analyze              └─> Background job  │
│          └─> 15-min timeout             └─> 30-min timeout  │
│          └─> Custom email               └─> DEFAULT_EMAIL   │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Frontend Interface (React + Tailwind)                       │
│  └─> Dark theme UI with glassmorphism effects               │
│  └─> Analysis window selector (7-35 days)                   │
│  └─> Real-time progress bar with 4 steps                    │
│  └─> Results display with expandable themes                 │
│  └─> Email recipient input (optional)                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
Groww App Review Analyzer/
├── frontend/                          # React TypeScript UI
│   ├── src/
│   │   ├── App.tsx                   # Main React component
│   │   ├── index.css                 # Tailwind + dark theme
│   │   └── ...
│   ├── dist/                         # Built static files
│   ├── package.json
│   └── vite.config.ts
│
├── layer1_scraping/                  # Google Play scraper
│   ├── __init__.py
│   ├── scraper.py
│   └── scraper_config.py
│
├── layer2_classification/            # Gemini LLM classification
│   ├── __init__.py
│   ├── classifier.py
│   └── classifier_config.py
│
├── layer3_insights/                  # MAP-REDUCE insight pipeline
│   ├── __init__.py
│   ├── insights.py
│   └── insights_config.py
│
├── layer4_email/                     # Email report generation
│   ├── __init__.py
│   ├── email_pulse_sender.py        # HTML email rendering
│   ├── email_config.py              # Email prompts & templates
│   └── scheduler.py                 # Auto-scheduler (APScheduler)
│
├── data/                             # Output files
│   ├── review_pulse_*.json          # Final insight reports
│   ├── review_classified_*.json     # Classified reviews
│   └── ...
│
├── logs/                             # Execution logs
│   ├── scheduler.log                # Scheduler execution
│   ├── orchestrator_*.log           # Full workflow logs
│   └── ...
│
├── app.py                            # FastAPI server
├── orchestrator.py                   # Workflow orchestrator
├── requirements.txt                  # Python dependencies
│
├── SCHEDULER_SETUP.md               # Scheduler quick start
├── SCHEDULER_CONFIG.md              # Scheduler configuration guide
├── SCHEDULER_TESTING.md             # Testing documentation
├── SCHEDULER_API.md                 # API endpoint reference
│
└── README.md                         # This file
```

---

## Installation

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- Google Gemini API key (free tier available at https://ai.google.dev)
- Git

### Setup Steps

**1. Clone the repository**
```bash
git clone https://github.com/Vishal0123456789/app-review-analyzer.git
cd app-review-analyzer
```

**2. Create and activate virtual environment (recommended)**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```powershell
# Windows PowerShell
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:SCHEDULER_ENABLED = "true"           # Optional, default: false
$env:SCHEDULER_DAY = "mon"                # Optional, default: mon
$env:SCHEDULER_HOUR = "8"                 # Optional, default: 8
$env:SCHEDULER_TIMEZONE = "UTC"           # Optional, default: UTC
```

Or create a `.env` file (git-ignored):
```
GEMINI_API_KEY=your-gemini-api-key
SCHEDULER_ENABLED=true
SCHEDULER_DAY=mon
SCHEDULER_HOUR=8
SCHEDULER_TIMEZONE=UTC
```

---

## Usage

### Start the Application

**Using uvicorn (recommended):**
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Application will be available at:**
- Frontend UI: http://localhost:8000
- API: http://localhost:8000/api

### Manual Analysis (Frontend)

1. Open http://localhost:8000 in your browser
2. Select analysis window (7-35 days)
3. (Optional) Enter email to receive report
4. Click "Analyze" button
5. Monitor real-time progress (4 steps, ~240 seconds)
6. Results displayed with theme breakdown and action items

### Automatic Scheduler

Enable automatic weekly analysis:

```powershell
$env:SCHEDULER_ENABLED = "true"
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Scheduler will automatically run every Monday at 8:00 AM UTC (configurable).

### Check Scheduler Status

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status"
$response.scheduler | ConvertTo-Json
```

Expected response:
```json
{
  "enabled": true,
  "running": true,
  "schedule": "mon 08:00",
  "timezone": "UTC",
  "next_run": "2025-12-08 08:00:00 UTC"
}
```

---

## API Endpoints

### 1. Analyze (Manual Trigger)

**POST** `/api/analyze`

Trigger analysis pipeline with custom parameters.

**Request:**
```json
{
  "window_days": 7,
  "email": "user@example.com"
}
```

**Parameters:**
- `window_days` (integer, required): Analysis window (7-35 days)
- `email` (string, optional): Additional recipient email

**Response:**
```json
{
  "status": "success",
  "message": "Weekly pulse generated and emails sent.",
  "window_days": 7,
  "pulse_file_name": "review_pulse_20251123_20251205.json",
  "pulse_data": {
    "start_date": "2025-11-23",
    "end_date": "2025-12-05",
    "top_themes": [...],
    "quotes": [...],
    "action_ideas": [...]
  }
}
```

### 2. Scheduler Status

**GET** `/api/scheduler-status`

Get scheduler configuration and next run time.

**Response:**
```json
{
  "status": "success",
  "scheduler": {
    "enabled": true,
    "running": true,
    "schedule": "mon 08:00",
    "timezone": "UTC",
    "next_run": "2025-12-08 08:00:00 UTC"
  }
}
```

### 3. Download Pulse

**GET** `/api/download-pulse?file=review_pulse_YYYYMMDD_YYYYMMDD.json`

Download previously generated pulse files.

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | Required | Google Gemini API key |
| `SCHEDULER_ENABLED` | false | Enable auto-scheduler |
| `SCHEDULER_DAY` | mon | Day of week (mon-sun) |
| `SCHEDULER_HOUR` | 8 | Hour (0-23) |
| `SCHEDULER_MINUTE` | 0 | Minute (0-59) |
| `SCHEDULER_TIMEZONE` | UTC | Timezone (e.g., Asia/Kolkata) |
| `SCHEDULER_WINDOW_DAYS` | 7 | Analysis window (7-35) |
| `DEFAULT_EMAIL` | agraharivishal19981@gmail.com | Default recipient |
| `PORT` | 8000 | Server port |
| `TO_EMAILS` | - | Additional recipients (comma-separated) |
| `SMTP_USERNAME` | - | SMTP username (for email sending) |
| `SMTP_PASSWORD` | - | SMTP password (for email sending) |

### Common Configurations

**Development (Manual Only):**
```powershell
$env:SCHEDULER_ENABLED = "false"
$env:GEMINI_API_KEY = "your-key"
```

**Production (With Scheduler - UTC):**
```powershell
$env:SCHEDULER_ENABLED = "true"
$env:SCHEDULER_DAY = "mon"
$env:SCHEDULER_HOUR = "8"
$env:SCHEDULER_TIMEZONE = "UTC"
$env:GEMINI_API_KEY = "your-key"
```

**Production (With Scheduler - Asia/Kolkata):**
```powershell
$env:SCHEDULER_ENABLED = "true"
$env:SCHEDULER_HOUR = "18"
$env:SCHEDULER_TIMEZONE = "Asia/Kolkata"
$env:GEMINI_API_KEY = "your-key"
```

---

## Email Report Format

Generated emails include:

1. **Header Bar**: Navy/teal gradient with "Weekly Product Pulse" title and date range
2. **Greeting**: Personalized opening ("Hi Team,")
3. **Key Insights Dashboard**: 3 colored priority cards
   - **CRITICAL** (Red): Execution & Performance issues
   - **HIGH** (Amber): UI & Feature Gaps
   - **FOCUS** (Yellow): Charges & Transparency concerns
4. **Detailed Analysis**: Per-theme sections with:
   - Theme sentiment summary
   - Key issues and quotes
   - User feedback bullets
5. **Action Roadmap**: Prioritized action items with timelines
6. **Content Limit**: Strictly under 350 words

---

## Testing

### Unit Tests

Run scheduler unit tests:
```bash
pip install pytest
pytest test_scheduler.py -v
```

### Manual Testing

Interactive test script:
```powershell
.\test_scheduler_manual.ps1
```

### API Testing

Check scheduler status:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/scheduler-status" | ConvertTo-Json
```

Trigger manual analysis:
```powershell
$body = @{ window_days = 7; email = "test@example.com" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

---

## Troubleshooting

### App won't start

**Issue**: Command exits silently
**Solution**: Use `uvicorn` explicitly instead of `python app.py`
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Scheduler not running

**Issue**: `running: false` in status endpoint
**Solution**: Verify `SCHEDULER_ENABLED=true` and check logs
```bash
Get-Content logs/scheduler.log | Select-String "Scheduler"
```

### GEMINI_API_KEY error

**Issue**: "GEMINI_API_KEY not set"
**Solution**: Set environment variable before starting
```powershell
$env:GEMINI_API_KEY = "your-api-key"
```

### Wrong timezone in scheduler

**Issue**: Next run time shows wrong timezone
**Solution**: Verify `SCHEDULER_TIMEZONE` and restart app
```powershell
$env:SCHEDULER_TIMEZONE = "Asia/Kolkata"  # or your timezone
```

### Email not sending

**Issue**: Analysis completes but no email received
**Solution**: Check logs for SMTP errors; verify SMTP credentials if sending to custom email

---

## Documentation Files

- **README.md** - This file; project overview and usage guide
- **SCHEDULER_SETUP.md** - Quick start guide for scheduler
- **SCHEDULER_CONFIG.md** - Detailed scheduler configuration reference
- **SCHEDULER_TESTING.md** - Comprehensive testing guide
- **SCHEDULER_API.md** - API endpoint documentation
- **SCHEDULER_IMPLEMENTATION_SUMMARY.md** - Architecture details
- **SCHEDULER_TESTING_QUICK_REFERENCE.md** - Quick test commands

---

## Technology Stack

### Backend
- **FastAPI** - REST API framework
- **Uvicorn** - ASGI server
- **Python 3.11** - Runtime
- **APScheduler** - Automated task scheduling
- **google-generativeai** - Gemini LLM integration
- **google-play-scraper** - Review scraping

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling (dark theme)
- **Vite** - Build tool

### Email
- **SMTP** - Email delivery
- **HTML/CSS** - Professional email formatting

---

## Security

### Credential Handling

⚠️ **IMPORTANT**: Never commit API keys or credentials to git!

- Store `GEMINI_API_KEY` only in environment variables
- Use `.env` files locally (add to `.gitignore`)
- For production, use secrets management (environment variables, secret managers, etc.)
- The `.gitignore` file already excludes common credential files

### Best Practices

- Never hardcode API keys in source code
- Rotate API keys periodically
- Use environment-specific credentials
- Monitor API usage for suspicious activity
- Restrict API key permissions to minimum required scope

---

## Performance

### Analysis Times

- **Layer 1** (Scraping): ~60 seconds
- **Layer 2** (Classification): ~60 seconds
- **Layer 3** (Insights): ~60 seconds
- **Layer 4** (Email): ~15 seconds
- **Total**: ~195 seconds (3 minutes)

### Optimization

- Layer 1-3 run in parallel where possible
- Frontend shows real-time progress
- Results cached for faster download
- Email generation optimized for <350 words

---

## Known Limitations

1. **Google Play Scraper**: Limited to ~100 reviews per request (throttling/pagination handled)
2. **Gemini API**: Free tier has quota limits; monitor usage
3. **Email Delivery**: Depends on SMTP server availability
4. **Timezone**: Must use standard timezone names (see APScheduler documentation)
5. **Frontend Progress**: Timing is approximation; may not match actual backend execution

---

## Contributing

Contributions are welcome! Please:

1. Create a feature branch from `main`
2. Make your changes with clear commit messages
3. Test thoroughly before submitting
4. Never commit API keys or credentials
5. Follow existing code style and patterns
6. Update documentation as needed

---

## Support

### Getting Help

- Check troubleshooting section above
- Review scheduler documentation files
- Check logs in `logs/` directory for detailed error messages
- API responses include error messages and status codes

### Common Issues

- **ModuleNotFoundError**: Run `pip install -r requirements.txt`
- **Port already in use**: Change PORT environment variable
- **Timezone errors**: Use standard timezone names from Python `pytz` library
- **API quota exceeded**: Wait for quota reset or upgrade Gemini plan

---

## License

This project analyzes reviews for the Groww app. Use accordance with Groww's terms of service.

---

## Contact

For questions or issues, please reach out to the development team or create an issue in the repository.

---

## Roadmap

Future enhancements:
- [ ] Multi-app support (not just Groww)
- [ ] Advanced filtering and segmentation
- [ ] Custom insight templates
- [ ] Webhook notifications
- [ ] Database storage (instead of JSON files)
- [ ] Advanced analytics dashboard
- [ ] Sentiment analysis enhancements
- [ ] Multi-language support

---

## Changelog

### v2.0.0 (2025-12-07)
- Added auto-scheduler with APScheduler
- Implemented professional HTML email reports
- Enhanced frontend with dark theme and progress tracking
- Added comprehensive testing suite
- Restructured email with Key Insights Dashboard
- Dual-mode orchestration (manual + automatic)

### v1.0.0 (Earlier)
- Initial release with 4-layer architecture
- Manual analysis triggering
- Basic email reports
- React frontend with Tailwind CSS
