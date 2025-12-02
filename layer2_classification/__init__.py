"""
Layer 2: Classification & Analysis

This layer is responsible for:
- Loading reviews from Layer 1 output
- Classifying reviews into 5 predefined themes using Gemini Pro LLM
- Determining sentiment (positive/negative/neutral)
- Validating LLM output and applying fallback logic
- Storing classified reviews in JSON/CSV format

Main Entry Point: review_classifier.py

Allowed Themes:
1. Execution & Performance
2. Payments & Withdrawals
3. Charges & Transparency
4. KYC & Access
5. UI & Feature Gaps
"""

from .classify_config import (
    ALLOWED_THEMES,
    THEME_KEYWORDS,
    THEME_PRECEDENCE,
    GEMINI_MODEL,
    BATCH_SIZE,
    CONFIDENCE_THRESHOLD,
    DEFAULT_THEME,
    INPUT_FILE,
    OUTPUT_JSON_TEMPLATE,
    OUTPUT_CSV_TEMPLATE
)

from .review_classifier import ReviewClassifier

__all__ = [
    'ReviewClassifier',
    'ALLOWED_THEMES',
    'THEME_KEYWORDS',
    'GEMINI_MODEL',
    'BATCH_SIZE',
    'CONFIDENCE_THRESHOLD',
]
