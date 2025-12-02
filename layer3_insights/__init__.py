"""
Layer 3: Insights & Weekly Pulse

This layer is responsible for:
- Loading classified reviews from Layer 2 output
- Grouping reviews by theme and selecting top 3
- MAP stage: Extract key points and quotes per theme (with chunking)
- REDUCE stage: Create ≤250-word weekly pulse note with actionable insights
- Storing theme summaries and final pulse note in JSON format

Main Entry Point: weekly_pulse_generator.py

Output Files:
- data/review_weekly_theme_summaries.json (aggregated theme-level summaries)
- data/review_weekly_pulse.json (final weekly pulse note with quotes and actions)
"""

from .weekly_pulse_generator import WeeklyPulseGenerator
from .insights_config import (
    INPUT_FILE,
    OUTPUT_THEME_SUMMARIES,
    OUTPUT_PULSE_NOTE,
    MAP_CHUNK_SIZE,
    TOP_THEMES_COUNT,
    MAX_QUOTES_PER_THEME,
    MAX_WORD_COUNT
)

__all__ = [
    'WeeklyPulseGenerator',
    'INPUT_FILE',
    'OUTPUT_THEME_SUMMARIES',
    'OUTPUT_PULSE_NOTE',
    'MAP_CHUNK_SIZE',
    'TOP_THEMES_COUNT',
]
