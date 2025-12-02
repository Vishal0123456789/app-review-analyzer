"""
Layer 4: Email & Communication

This layer is responsible for:
- Loading the weekly pulse JSON from Layer 3 output
- Generating a subject line using Gemini LLM
- Generating an email body tailored to Product/Growth, Support, and Leadership audiences
- Sending the email to configured recipients
- Logging the send status with metadata

Main Entry Point: email_pulse_sender.py

Output Files:
- data/email_send_log_{week_start}.json (email send status log with metadata)

Configuration:
- email_config.py (product name, email addresses, SMTP settings)
"""

from .email_pulse_sender import EmailPulseSender
from .email_config import (
    INPUT_PULSE_FILE,
    OUTPUT_LOG_TEMPLATE,
    PRODUCT_NAME,
    FROM_EMAIL,
    TO_EMAILS,
    USE_MOCK_SEND
)

__all__ = [
    'EmailPulseSender',
    'INPUT_PULSE_FILE',
    'OUTPUT_LOG_TEMPLATE',
    'PRODUCT_NAME',
    'FROM_EMAIL',
    'TO_EMAILS',
]
