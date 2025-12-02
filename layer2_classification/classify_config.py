# Classification Configuration

ALLOWED_THEMES = [
    "Execution & Performance",
    "Payments & Withdrawals",
    "Charges & Transparency",
    "KYC & Access",
    "UI & Feature Gaps"
]

# Keyword patterns for fallback classification
THEME_KEYWORDS = {
    "Execution & Performance": [
        "execution", "pending", "order", "delay", "chart", "lag", "crash", "freeze",
        "stuck", "hang", "slow", "not updating", "ltp", "f&o", "strike", "option chain",
        "position", "not visible", "something went wrong", "error", "price not refreshing",
        "blocking", "buy-sell", "app lag", "app freeze", "app crash", "technical issue",
        "glitch", "bug", "not working"
    ],
    "Payments & Withdrawals": [
        "payment", "debit", "money", "not reflected", "refund", "delay", "withdrawal",
        "taking days", "wallet", "balance", "incorrect", "decreasing", "settlement",
        "sale settlement", "auto-deduction", "unexplained", "pending", "charged"
    ],
    "Charges & Transparency": [
        "charge", "brokerage", "expensive", "cost", "fee", "hidden", "unexpected",
        "profit", "settled", "zerodha", "dhan", "competitor", "scalper"
    ],
    "KYC & Access": [
        "kyc", "aadhaar", "biometric", "verification", "incomplete", "blocking",
        "investment", "trading", "renew", "registration", "loop", "account",
        "reactivate", "inactivity", "pan"
    ],
    "UI & Feature Gaps": [
        "ui", "feature", "confusing", "oi", "etf", "stock", "tool", "fibonacci",
        "scalping", "watchlist", "statement", "unprofessional", "unformatted",
        "sip", "pause", "resume", "missing", "gap", "interface", "design"
    ]
}

# Precedence order for classification
THEME_PRECEDENCE = [
    "Execution & Performance",
    "Payments & Withdrawals",
    "Charges & Transparency",
    "KYC & Access",
    "UI & Feature Gaps"
]

# LLM Configuration
GEMINI_MODEL = "gemini-2.5-flash"
BATCH_SIZE = 10  # Reviews per LLM call (reduced from 20 to avoid timeout)
MAX_RETRIES = 2
CONFIDENCE_THRESHOLD = 0.4
FALLBACK_CONFIDENCE = 0.45
DEFAULT_THEME = "UI & Feature Gaps"  # Default to UI & Feature Gaps (most common fallback)

# Input/Output files
INPUT_FILE = "data/review_transformed_20251030_20251127.json"
OUTPUT_JSON_TEMPLATE = "data/review_classified_20251030_20251127.json"
OUTPUT_CSV_TEMPLATE = "data/review_classified_20251030_20251127.csv"

# LLM Prompt template
LLM_SYSTEM_PROMPT = """You are a review classifier for a trading/investment app. For each review, classify into exactly ONE theme and determine sentiment.

Themes:
- Execution & Performance: Order execution delays, chart updates, app lag/freeze/crashes, F&O issues, position visibility, "something went wrong" errors, price refreshing issues
- Payments & Withdrawals: Money debited but not reflected, refund delays, withdrawal timing (3-4 days), wallet balance issues, settlement delays, auto-deductions
- Charges & Transparency: High brokerage, unexpected/hidden charges, profit settlement mismatches, pricing complaints, fee comparisons
- KYC & Access: Re-KYC failures, "KYC incomplete" blocking, KYC renewal issues, registration loops, account reactivation problems
- UI & Feature Gaps: Confusing F&O UI, ETF mixed with stocks, missing tools (Fibonacci, scalping), watchlist accessibility, unprofessional statements, SIP pause/resume missing

Sentiment classification:
- positive: Review expresses satisfaction, praise, or positive experience
- negative: Review expresses dissatisfaction, complaints, or problems
- neutral: Review is factual without clear positive or negative tone

Classification rules:
1. Order/execution/pending/delay/chart/lag/freeze/crash/F&O → Execution & Performance
2. Money/debit/payment/refund/withdrawal/wallet/balance → Payments & Withdrawals
3. Charge/brokerage/cost/fee/expensive/profit → Charges & Transparency
4. KYC/Aadhaar/verification/incomplete/blocking → KYC & Access
5. UI/feature/confusing/missing/tool/watchlist → UI & Feature Gaps

Precedence (if multiple signals): Execution & Performance > Payments & Withdrawals > Charges & Transparency > KYC & Access > UI & Feature Gaps

Return ONLY valid JSON array. No prose, markdown, or explanation. Each object must have:
- review_id: from input
- review_theme: one of the themes above
- sentiment: positive, negative, or neutral
- confidence: 0.0-1.0 (0.7-1.0 for clear cases)
- reason: 1-2 word explanation

Example output:
[
  {"review_id":"r1","review_theme":"Payments & Withdrawals","sentiment":"negative","confidence":0.95,"reason":"money debited"},
  {"review_id":"r2","review_theme":"Execution & Performance","sentiment":"negative","confidence":0.92,"reason":"app crashes"}
]"""

LLM_USER_PROMPT_TEMPLATE = """Classify these reviews:

{reviews_json}

Return ONLY the JSON array with classifications. No other text."""

# Logging
from datetime import datetime
LOG_DATE = datetime.now().strftime('%Y%m%d')
LOG_FILE = f"logs/classifier_{LOG_DATE}.log"
LOG_LEVEL = "INFO"
