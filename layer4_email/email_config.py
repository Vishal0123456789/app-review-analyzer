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
FROM_EMAIL = "agraharivishal19981@gmail.com"
# Read TO_EMAILS from environment variable (comma-separated), default to FROM_EMAIL if not set
TO_EMAILS_ENV = os.getenv('TO_EMAILS', "agraharivishal19981@gmail.com")
TO_EMAILS = [email.strip() for email in TO_EMAILS_ENV.split(',')]
BCC_EMAIL = None  # Optional: BCC email address

# SMTP configuration (use environment variables in production)
# SMTP configuration (use environment variables in production)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
# SMTP credentials should come from environment variables:
# SMTP_USERNAME = os.getenv('SMTP_USERNAME')
# SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# For testing: you can use print instead of sending
# For testing: you can use print instead of sending
USE_MOCK_SEND = os.getenv("USE_MOCK_SEND", "False").lower() == "true"

# LLM Configuration
GEMINI_MODEL = "gemini-2.5-flash"

# Subject line prompt template
SUBJECT_PROMPT_TEMPLATE = """Generate a professional, urgent email subject line for a product pulse email.
Product: {product_name}
Period: {start_date} to {end_date}

Format EXACTLY like this example:
🚨 Groww App Pulse Deep Dive: [Top 3 Theme Names] ({start_date} - {end_date})

Instructions:
- Start with 🚨 emoji
- Include product name
- List the 3 top themes/pain points briefly
- Include the date range in parentheses
- Keep total length under 75 characters

Return ONLY the subject line, no quotes, no explanation."""

# Email body prompt template
EMAIL_BODY_PROMPT_TEMPLATE = """You are transforming a plaintext product pulse into a professional, modern Markdown-formatted email that looks like a data dashboard.

Input (review_pulse JSON):
{pulse_json}

Metadata:
- Product: {product_name}
- Period: {start_date} to {end_date}

=== OUTPUT REQUIREMENTS ===

Your task is to create a Markdown email following this EXACT structure:

**SECTION 1: OPENING (Greeting & Context)**
- Start with: "Hi Team,"
- Follow immediately with a single paragraph (2-3 sentences max) establishing:
  * The purpose: "This is the weekly product pulse for {product_name}"
  * The time period: "from {start_date} to {end_date}"
  * The urgency: "Immediate attention is required to address critical user experience issues."
- NO repeated content
- Keep professional and concise

---

**SECTION 2: KEY INSIGHTS DASHBOARD (Critical - This is the visual hook)**
- Create a 3-column Markdown table with headers: "**Theme**", "**Core Sentiment**", "**Priority Signal**"
- Add exactly 3 rows (one for each top theme from the input)
- For Priority Signal, use ONLY: CRITICAL, HIGH, or FOCUS (no emojis in table cells)
- Ensure table formatting is clean and professional
- This table is the immediate visual summary that tells the reader the status in 3 seconds

---

**SECTION 3: THEMATIC SECTIONS (Detailed Analysis)**
- For each top theme (in order), create a section with:
  * Heading: ### 1. [Theme Name] ([Specific Impact/Subtitle])
  * Body: 1-2 paragraphs explaining the issue and user impact
  * Sub-bullets: Use • (bullet) with relevant issues (specific data, not generic)
  * User Quotes: Include 1-2 actual quotes from the input in format: > "quote text"
  * Blank line after each theme section

**SECTION 4: ACTION ROADMAP (Recommended Action Items)**
- Use heading: ### Recommended Action Items
- Brief intro: "Address these critical pain points with the following priorities:"
- For each action item:
  * Line 1: **[Action Title]** (in bold)
  * Line 2: Brief description of what needs to be done
  * Line 3: **Target:** [Timeline, e.g., "Next 2 Sprints"]
  * Blank line between items

**SECTION 5: CLOSING**
- End with an engaging question that prompts decision-making
- Example: "Which action item should we prioritize first?"
- Keep it conversational and action-oriented

=== FORMATTING RULES ===

1. Content Preservation: Use EXACT text from input (don't paraphrase)
2. NO Duplicate Content: Each section appears exactly once with unique content
3. Markdown Features:
   - Use ### for main theme headings only (3 times max for themes)
   - Use > for quotes (blockquote format)
   - Use • for bullet points
   - Use **text** for bold
   - Use --- for horizontal rules (section separators)
   - Use | for table formatting
4. Professional tone with strategic emphasis
5. Length: Keep total under 350 words
6. NO emojis in body text (they're handled in HTML rendering)

=== EXAMPLE OUTPUT STRUCTURE ===

Hi Team,

This is the weekly product pulse for Groww Android App from 2025-11-30 to 2025-12-05. This consolidates critical user feedback and insights across our platform. Immediate attention is required to address core user experience issues.

---

| **Theme** | **Core Sentiment** | **Priority Signal** |
|---|---|---|
| Execution & Performance | Users experiencing crashes and delays | CRITICAL |
| UI & Feature Gaps | Navigation and data visibility issues | HIGH |
| Charges & Transparency | Lack of clarity on fees | FOCUS |

---

### 1. Execution & Performance (Stability & Accuracy Concerns)

[2-3 paragraphs explaining the issue, user impact, and context]

• [Specific issue 1]
• [Specific issue 2]
• [Specific issue 3]

> "User quote demonstrating the issue"

### 2. UI & Feature Gaps (User Navigation & Discovery)

[Content for theme 2...]

### Recommended Action Items

Address these critical pain points with the following priorities:

**Action Item 1 Title**
Brief description of what needs to be done.
**Target:** Next 2 Sprints

**Action Item 2 Title**
Brief description.
**Target:** Next 3 Sprints

Which action item should we prioritize first?

=== END REQUIREMENTS ===

Generate the complete email now in Markdown format."""

# Logging
from datetime import datetime
LOG_DATE = datetime.now().strftime('%Y%m%d')
LOG_FILE = f"logs/email_{LOG_DATE}.log"
LOG_LEVEL = "INFO"
