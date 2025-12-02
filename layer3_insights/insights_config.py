# Layer 3: Insights & Weekly Pulse Configuration

# Input/Output files - will be set dynamically by orchestrator
INPUT_FILE = None  # Set at runtime by orchestrator
OUTPUT_THEME_SUMMARIES = None  # Will be updated with date at runtime
OUTPUT_PULSE_NOTE = None  # Will be updated with date at runtime

# Processing parameters
MAP_CHUNK_SIZE = 20  # Reviews per chunk for LLM processing
TOP_THEMES_COUNT = 3  # Select top 3 themes by review count
MAX_QUOTES_PER_THEME = 10  # Maximum quotes to aggregate per theme
MAX_WORD_COUNT = 250  # Maximum words in final pulse note

# LLM Configuration
GEMINI_MODEL = "gemini-2.5-flash"
BATCH_SIZE = 20
MAX_RETRIES = 1

# Allowed themes (same as Layer 2)
ALLOWED_THEMES = [
    "Execution & Performance",
    "Payments & Withdrawals",
    "Charges & Transparency",
    "KYC & Access",
    "UI & Feature Gaps"
]

# MAP STAGE PROMPT
MAP_PROMPT_TEMPLATE = """You are summarizing user feedback about a trading and investing app.

Theme: {theme_name}
Reviews (already cleaned, no direct PII):
{reviews_list}

Tasks:
1. Extract 3–5 key points about this theme in a neutral, factual tone.
2. Identify up to 3 short, vivid quotes that capture the sentiment.
   - Do NOT include names, usernames, emails, or IDs.
   - If a quote contains PII or specific identifiers, rewrite it to keep meaning but remove the PII.
3. Return ONLY valid JSON in this format:
{{
  "theme": "{theme_name}",
  "key_points": ["...", "..."],
  "candidate_quotes": ["...", "..."]
}}
Keep everything concise. Avoid marketing fluff."""

# REDUCE STAGE PROMPT
REDUCE_PROMPT_TEMPLATE = """You are a Product Manager writing an app insights pulse for an investing & trading app.
Time window: {start_date} to {end_date}

Top themes with summaries:
{themes_json}

Your tasks:
1. Identify the Top 3 themes (already filtered for you).
2. Pick 3 short, vivid user quotes total across these themes:
   - Quotes must be anonymized (no names, usernames, emails, IDs).
   - If any quote contains PII, rewrite it to keep meaning but remove identifiers.
3. Propose 3 concrete action ideas (product or process) that directly respond to the feedback.
4. Write a ≤250-word, bullet-heavy, scannable note in this structure:
- Heading: "Weekly App Review Pulse ({start_date}–{end_date})"
- Section: "Top Themes"
  - • Theme 1 – 1–2 bullets on what users are saying
  - • Theme 2 – 1–2 bullets
  - • Theme 3 – 1–2 bullets
- Section: "User Voice (Quotes)"
  - • "quote 1"
  - • "quote 2"
  - • "quote 3"
- Section: "Action Ideas"
  - • Action idea 1
  - • Action idea 2
  - • Action idea 3

Constraints:
- Max 250 words total.
- Use bullets, short sentences, and no marketing language.
- Do NOT include any names, usernames, emails, or IDs.
- Do NOT invent features; base actions on the themes and key points.

Return ONLY valid JSON:
{{
  "start_date": "{start_date}",
  "end_date": "{end_date}",
  "top_themes": [
    {{"theme": "...", "summary_bullets": ["...", "..."]}},
    {{"theme": "...", "summary_bullets": ["...", "..."]}},
    {{"theme": "...", "summary_bullets": ["...", "..."]}}
  ],
  "quotes": ["...", "...", "..."],
  "action_ideas": ["...", "...", "..."],
  "note_markdown": "full note in markdown, ≤250 words"
}}"""

# Logging
from datetime import datetime
LOG_DATE = datetime.now().strftime('%Y%m%d')
LOG_FILE = f"logs/insights_{LOG_DATE}.log"
LOG_LEVEL = "INFO"
