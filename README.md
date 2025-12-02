# App Review Insights Analyzer

A four-layer architecture for automated scraping, classification, insight generation, and email delivery of Google Play app reviews. Includes a modern React web interface for easy interaction.

## Quick Start

### Option 1: Command Line (Recommended for automation)
```powershell
# Set required environment variables
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:TO_EMAILS = "recipient@example.com"

# Run the complete workflow
cd "c:\Users\satis\Milestone 2"
python orchestrator.py --window-days 28
```

### Option 2: Web Interface (Recommended for interactive use)

**Terminal 1 - Start Backend:**
```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key"
cd "c:\Users\satis\Milestone 2"
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```powershell
cd "c:\Users\satis\Milestone 2\frontend"
npm run dev
```

Then open: **http://localhost:5173** in your browser

---

## Project Structure

```
Milestone 2/
├── orchestrator.py                    # MAIN ENTRY POINT - Run all 4 layers
├── app.py                             # FastAPI backend server for web interface
│
├── frontend/                          # React web interface
│   ├── src/
│   │   ├── App.tsx                    # Main React component
│   │   ├── main.tsx                   # React entry point
│   │   └── App.css                    # Tailwind styles
│   ├── package.json                   # Dependencies
│   ├── vite.config.ts                 # Vite build config
│   ├── tailwind.config.js             # Tailwind CSS config
│   ├── index.html                     # HTML template
│   └── README.md                      # Frontend documentation
│
├── layer1_scraping/                   # Layer 1: Fetch reviews from Google Play
│   ├── __init__.py
│   ├── scheduler_runner.py            # ReviewScheduler class
│   └── review_processor.py            # PII redaction, text cleaning, normalization
│
├── layer2_classification/             # Layer 2: Classify reviews into 5 themes + sentiment
│   ├── __init__.py
│   ├── classify_config.py             # Themes, LLM config, prompts
│   └── review_classifier.py           # ReviewClassifier class using Gemini LLM
│
├── layer3_insights/                   # Layer 3: Generate weekly pulse insights
│   ├── __init__.py
│   ├── insights_config.py             # MAP-REDUCE pipeline config
│   └── weekly_pulse_generator.py      # WeeklyPulseGenerator class
│
├── layer4_email/                      # Layer 4: Generate and send weekly emails
│   ├── __init__.py
│   ├── email_config.py                # Email templates, SMTP config
│   └── email_pulse_sender.py          # EmailPulseSender class
│
├── data/                              # All output files stored here
│   ├── review_transformed_*.json          # Layer 1 raw reviews
│   ├── review_transformed_*.csv
│   ├── review_classified_*.json           # Layer 2 classified reviews
│   ├── review_classified_*.csv
│   ├── review_theme_summaries_*.json      # Layer 3 theme summaries
│   ├── review_pulse_*.json                # Layer 3 final pulse
│   ├── email_send_log_*.json              # Layer 4 email logs
│   └── workflow_summary_*.json            # Orchestrator execution summary
│
├── logs/                              # All logs stored here (date-based filenames)
│   ├── scheduler_YYYYMMDD.log         # Layer 1
│   ├── classifier_YYYYMMDD.log        # Layer 2
│   ├── insights_YYYYMMDD.log          # Layer 3
│   ├── email_YYYYMMDD.log             # Layer 4
│   └── orchestrator_YYYYMMDD.log      # Orchestrator
│
├── requirements.txt                   # Python dependencies (core)
├── requirements_web.txt               # Python dependencies (web)
├── README.md                          # This file
└── .gitignore
```

## Four-Layer Architecture

### Layer 1: Data Scraping & Storage
**What it does:** Fetches ~4000 reviews from Google Play, applies filters (relevance > 0, last 28 days), redacts PII, removes emojis, normalizes text.

**Output:**
- `review_transformed_YYYYMMDD_YYYYMMDD.json` (raw reviews)
- `review_transformed_YYYYMMDD_YYYYMMDD.csv`
- `logs/scheduler_YYYYMMDD.log`

**Files:**
- `layer1_scraping/scheduler_runner.py` → ReviewScheduler class
- `layer1_scraping/review_processor.py` → Processing logic

---

### Layer 2: Classification & Analysis
**What it does:** Classifies reviews into 5 predefined themes using Gemini LLM, determines sentiment (positive/negative/neutral), calculates confidence scores.

**5 Themes:**
1. Execution & Performance (order delays, crashes, lag)
2. Payments & Withdrawals (payment issues, refund delays)
3. Charges & Transparency (brokerage complaints, hidden fees)
4. KYC & Access (account access, re-KYC issues)
5. UI & Feature Gaps (interface issues, missing tools)

**Output:**
- `review_classified_YYYYMMDD_YYYYMMDD.json` (classified reviews)
- `review_classified_YYYYMMDD_YYYYMMDD.csv`
- `logs/classifier_YYYYMMDD.log`

**Files:**
- `layer2_classification/review_classifier.py` → ReviewClassifier class
- `layer2_classification/classify_config.py` → Config + themes + prompts

---

### Layer 3: Insights & Weekly Pulse
**What it does:** Uses MAP-REDUCE pipeline to aggregate reviews by theme, extract key points and quotes, generate a ≤250-word weekly pulse note with action ideas.

**Output:**
- `review_theme_summaries_YYYYMMDD.json` (theme aggregations)
- `review_pulse_YYYYMMDD.json` (final pulse note)
- `logs/insights_YYYYMMDD.log`

**Files:**
- `layer3_insights/weekly_pulse_generator.py` → WeeklyPulseGenerator class
- `layer3_insights/insights_config.py` → Config + MAP-REDUCE prompts

---

### Layer 4: Email Generation & Delivery
**What it does:** Generates email subject and body using Gemini LLM, sends via SMTP (or mock mode for testing).

**Output:**
- `email_send_log_YYYY-MM-DD.json` (email metadata)
- `logs/email_YYYYMMDD.log`

**Files:**
- `layer4_email/email_pulse_sender.py` → EmailPulseSender class
- `layer4_email/email_config.py` → Config + email templates

---

## Architecture Overview

## Usage

### Web Interface (Easiest Way)

A modern, responsive React web interface is available for interactive analysis.

**Features:**
- 🎨 Clean, intuitive UI with real-time status
- 📱 Fully responsive (desktop & mobile)
- 🔍 Select analysis window (7-56 days)
- 📧 Optional email recipient (in addition to default)
- 📥 Download pulse results as JSON
- ⚡ Live analysis progress indicator

**Setup:**
```powershell
# Install frontend dependencies (first time only)
cd frontend
npm install
```

**Run (2 terminals):**

*Terminal 1 - Backend:*
```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key"
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

*Terminal 2 - Frontend:*
```powershell
cd frontend
npm run dev
```

Open: **http://localhost:5173**

---

### Command Line (Automation)

For scheduled runs or CI/CD pipelines.
```powershell
# Set required environment variable
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:TO_EMAILS = "recipient@example.com"  # Optional, defaults to sender

# Run all 4 layers in sequence
cd "c:\Users\satis\Milestone 2"
python orchestrator.py
```

### Custom Options
```powershell
# Run with custom date window (default: 28 days)
python orchestrator.py --window-days 14

# Run with 7-day lookback
python orchestrator.py --window-days 7

# Run with 60-day lookback
python orchestrator.py --window-days 60
```

### What Happens
When you run `orchestrator.py`:
1. **Layer 1** (10-15 sec): Scrapes reviews, applies filters, saves to `data/`
2. **Layer 2** (30-60 sec): Classifies reviews using LLM, saves to `data/`
3. **Layer 3** (20-30 sec): Generates theme summaries and pulse note, saves to `data/`
4. **Layer 4** (10-20 sec): Creates and sends email, saves log to `data/`
5. **Orchestrator** saves execution summary to `data/workflow_summary_*.json`

**Total time:** ~2-3 minutes per run

### Output Files
After running on Dec 1, 2025, you'll have:

**Data (in `data/` directory):**
- `review_transformed_20251104_20251201.json` (Layer 1)
- `review_transformed_20251104_20251201.csv` (Layer 1)
- `review_classified_20251104_20251201.json` (Layer 2)
- `review_classified_20251104_20251201.csv` (Layer 2)
- `review_theme_summaries_20251201.json` (Layer 3)
- `review_pulse_20251201.json` (Layer 3)
- `email_send_log_2025-12-01.json` (Layer 4)
- `workflow_summary_2025-12-01_HH-MM-SS.json` (Orchestrator)

**Logs (in `logs/` directory):**
- `scheduler_20251201.log` (Layer 1)
- `classifier_20251201.log` (Layer 2)
- `insights_20251201.log` (Layer 3)
- `email_20251201.log` (Layer 4)
- `orchestrator_20251201.log` (Orchestrator)


## Data Flow

```
Google Play Store API (~4000 reviews)
         ↓
LAYER 1: Scraping & Storage (10-15 sec)
  ├─ Filter: relevance > 0 (thumbsUpCount)
  ├─ Filter: last 28 days
  ├─ PII redaction (emails, phone, PAN, Aadhaar)
  ├─ Emoji removal
  ├─ Text normalization
  └─ Output: ~150-200 clean reviews
         ↓
LAYER 2: Classification & Analysis (30-60 sec)
  ├─ Classify into 5 themes (Gemini LLM)
  ├─ Determine sentiment (positive/negative/neutral)
  ├─ Calculate confidence (0.0-1.0)
  └─ Output: ~150-200 classified reviews
         ↓
LAYER 3: Insights & Weekly Pulse (20-30 sec)
  ├─ Group by theme
  ├─ MAP stage: Extract key points & quotes per theme
  ├─ REDUCE stage: Generate final pulse note
  └─ Output: Theme summaries + pulse note (≤250 words)
         ↓
LAYER 4: Email Generation & Delivery (10-20 sec)
  ├─ Generate email subject (Gemini LLM)
  ├─ Generate email body (Gemini LLM, formatted for 3 audiences)
  ├─ Send via SMTP or mock mode
  └─ Output: Email log + receipt
         ↓
OrchestratorSummary
  └─ Save execution summary (status, timestamps, file paths)
```

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Reviews (Layer 1) | 170 |
| Themes | 5 (predefined) |
| Sentiment Types | 3 (positive, negative, neutral) |
| Average Confidence | 91.7% |
| Fallback Rate | 0% |

### Theme Distribution
- Execution & Performance: 35.9% (61 reviews)
- UI & Feature Gaps: 34.1% (58 reviews)
- Charges & Transparency: 12.4% (21 reviews)
- Payments & Withdrawals: 11.2% (19 reviews)
- KYC & Access: 6.5% (11 reviews)

### Sentiment Distribution
- Negative: 67.6% (115 reviews)
- Positive: 20.0% (34 reviews)
- Neutral: 12.4% (21 reviews)

## Configuration

### Required: Gemini API Key
```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key-here"
```
Get your key: https://aistudio.google.com/app/apikeys

### Optional: Email Recipients
```powershell
# For command line (env var)
$env:TO_EMAILS = "recipient1@example.com,recipient2@example.com"

# For web interface: enter in the form field (optional)
# Always sends to default: agraharivishal19981@gmail.com
```

### Optional: SMTP Credentials (for real email sending)
```powershell
$env:SMTP_USERNAME = "your-gmail@gmail.com"
$env:SMTP_PASSWORD = "your-gmail-app-password"
# Uses mock mode if not set (logs email instead of sending)
```

### Layer-Specific Configuration

**Layer 1** (`layer1_scraping/scheduler_runner.py`):
- LOOKBACK_DAYS = 28 (last 4 weeks)
- MIN_WORD_COUNT = 10 (filter short reviews)
- APP_ID = 'com.nextbillion.groww'

**Layer 2** (`layer2_classification/classify_config.py`):
- GEMINI_MODEL = 'gemini-2.5-flash'
- BATCH_SIZE = 20 (reviews per LLM call)
- CONFIDENCE_THRESHOLD = 0.4

**Layer 3** (`layer3_insights/insights_config.py`):
- MAP_CHUNK_SIZE = 20 (reviews per chunk)
- TOP_THEMES_COUNT = 3 (top themes in pulse)
- MAX_WORD_COUNT = 250 (pulse note limit)

**Layer 4** (`layer4_email/email_config.py`):
- FROM_EMAIL = 'agraharivishal1998@gmail.com'
- TO_EMAILS = (from env var)
- USE_MOCK_SEND = False (set to True to skip email sending)

## Output Schemas

### Layer 1 Output (Raw Reviews)
```json
{
  "review_id": "uuid",
  "date": "2025-12-01",
  "week_start_date": "2025-11-24",
  "week_end_date": "2025-11-30",
  "rating": 4,
  "title": "17.96.7",
  "text": "original text with [PII_REDACTED]",
  "clean_text": "lowercase normalized text",
  "relevance": 5,
  "source": "google_play"
}
```

### Layer 2 Output (Classified Reviews)
```json
{
  "review_id": "uuid",
  "date": "2025-12-01",
  "rating": 4,
  "title": "17.96.7",
  "text": "original text",
  "clean_text": "normalized text",
  "sentiment": "positive",
  "review_theme": "Execution & Performance",
  "confidence": 0.92,
  "reason": "app crashes",
  "llm_suggested_theme": null,
  "fallback_applied": false
}
```

### Layer 3 Output (Weekly Pulse)
```json
{
  "start_date": "2025-11-04",
  "end_date": "2025-12-01",
  "top_themes": [
    {"theme": "Execution & Performance", "summary_bullets": [...]},
    {"theme": "UI & Feature Gaps", "summary_bullets": [...]},
    {"theme": "Payments & Withdrawals", "summary_bullets": [...]}
  ],
  "quotes": ["user quote 1", "user quote 2", "user quote 3"],
  "action_ideas": ["action 1", "action 2", "action 3"],
  "note_markdown": "Weekly App Review Pulse... (≤250 words)"
}
```

### Layer 4 Output (Email Log)
```json
{
  "week_start_date": "2025-11-04",
  "week_end_date": "2025-12-01",
  "product_name": "Groww Android App",
  "to": ["recipient@example.com"],
  "from": "sender@example.com",
  "subject": "Weekly Product Pulse – Groww (2025-11-04–2025-12-01)",
  "sent_at": "2025-12-01T14:30:45.123456",
  "status": "success|mock",
  "error_message": null
}
```

## Scheduling for Production

### Windows Task Scheduler
Create a batch file `run_weekly_pulse.bat`:
```batch
@echo off
cd /d "c:\Users\satis\Milestone 2"
set GEMINI_API_KEY=your-api-key
set TO_EMAILS=recipient@example.com
python orchestrator.py >> logs\scheduled_runs.log 2>&1
```

Then schedule it in Task Scheduler:
1. Open `taskschd.msc`
2. Create Basic Task
3. Trigger: Weekly (e.g., Monday 8:00 AM)
4. Action: Run `run_weekly_pulse.bat`

### Linux/Mac Cron Job
```bash
# Edit crontab
crontab -e

# Add line (runs every Monday at 8 AM)
0 8 * * 1 cd /path/to/Milestone\ 2 && GEMINI_API_KEY=your-key TO_EMAILS=recipient@email.com python orchestrator.py >> logs/scheduled_runs.log 2>&1
```

---

## Logging

All logs are stored in `logs/` directory with date-based filenames:
- `scheduler_YYYYMMDD.log` - Layer 1 execution
- `classifier_YYYYMMDD.log` - Layer 2 execution
- `insights_YYYYMMDD.log` - Layer 3 execution
- `email_YYYYMMDD.log` - Layer 4 execution
- `orchestrator_YYYYMMDD.log` - Main orchestrator

**Check logs:**
```powershell
# View latest orchestrator log
Get-Content logs/orchestrator_*.log -Tail 50

# View latest layer logs
Get-Content logs/scheduler_*.log -Tail 20
```

## Documentation

For more details, check:
- `README.md` - This file (main documentation)
- `frontend/README.md` - Frontend setup and development guide
- Inline code comments in layer files for implementation details

## Dependencies

- `google-play-scraper` - Google Play API
- `google-generativeai` - Gemini Pro LLM
- `requests` - HTTP client
- `python-dateutil` - Date utilities

See `requirements.txt` for full list and versions.

## Future Enhancements

- Multi-label classification (reviews in multiple themes)
- Real-time streaming (Kafka, Pub/Sub)
- Dashboard integration (Grafana, Tableau)
- Alert system for critical issues
- Trend analysis and anomaly detection

## License

Proprietary - Internal Use Only

## Support

For issues or questions, refer to the documentation in `docs/` directory.
