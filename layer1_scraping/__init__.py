"""
Layer 1: Data Scraping & Storage

This layer is responsible for:
- Fetching reviews from Google Play Store
- Applying filters (relevance > 0, last 28 days)
- Processing reviews (PII redaction, emoji removal, text normalization)
- Storing processed reviews in JSON/CSV format

Main Entry Point: scheduler_runner.py
"""

from .scheduler_runner import ReviewScheduler

__all__ = [
    'ReviewScheduler',
]
