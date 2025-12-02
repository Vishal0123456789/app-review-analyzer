# Layer 4: Email Configuration

import os

# Input file from Layer 3 - will be passed dynamically from orchestrator
INPUT_PULSE_FILE = None  # Set at runtime by orchestrator

# Output log file - will use start date from pulse data
OUTPUT_LOG_TEMPLATE = "data/email_send_log_{week_start}_{week_end}.json"

# Product metadata
PRODUCT_NAME = "Groww Android App"
PRODUCT_CONTEXT = "A mobile trading and investment application"

# Email configuration
FROM_EMAIL = "agraharivishal1998@gmail.com"
# Read TO_EMAILS from environment variable (comma-separated), default to FROM_EMAIL if not set
TO_EMAILS_ENV = os.getenv('TO_EMAILS', "agraharivishal1998@gmail.com")
TO_EMAILS = [email.strip() for email in TO_EMAILS_ENV.split(',')]
BCC_EMAIL = None  # Optional: BCC email address

# SMTP configuration (use environment variables in production)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True
# SMTP credentials should come from environment variables:
# SMTP_USERNAME = os.getenv('SMTP_USERNAME')
# SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# For testing: you can use print instead of sending
USE_MOCK_SEND = False  # Set to False to actually send emails

# LLM Configuration
GEMINI_MODEL = "gemini-2.5-flash"

# Subject line prompt template
SUBJECT_PROMPT_TEMPLATE = """You are generating a concise, informative subject line for a weekly internal product pulse email.
Product name: {product_name}
Week: {start_date} to {end_date}

Return ONLY a single line of plain text, no quotes, no extra explanation.
Format: Weekly Product Pulse – product_name (start_date–end_date)"""

# Email body prompt template
EMAIL_BODY_PROMPT_TEMPLATE = """You are drafting an internal email sharing the latest product pulse.

Audience:
- Product & Growth: want to see what to fix or double down on.
- Support: want to know what to acknowledge and celebrate.
- Leadership: want a quick pulse, key risks, and wins.

Input (review_weekly_pulse JSON):
{pulse_json}

Metadata:
- Product name: {product_name}
- Time window: {start_date} to {end_date}

Tasks:
- Write an email BODY only (no subject line).
- Structure:
  1) 2–3 line intro explaining the time window and the product/program.
  2) Embed the weekly pulse note in a clean, scannable format:
     - Title: "Weekly App Review Pulse"
     - Short overview (1–2 bullets)
     - Bulleted Top 3 themes
     - Bulleted 3 user quotes
     - Bulleted 3 action ideas
  3) End with a short closing line (1–2 sentences).

Constraints:
- Professional, neutral tone with a hint of warmth.
- No names, emails, or IDs. If present in quotes, anonymize generically (e.g., 'a user', 'one investor', 'one participant').
- Keep the whole email under 350 words.
- Output PLAIN TEXT only (no HTML, no markdown, no extra JSON)."""

# Logging
from datetime import datetime
LOG_DATE = datetime.now().strftime('%Y%m%d')
LOG_FILE = f"logs/email_{LOG_DATE}.log"
LOG_LEVEL = "INFO"
