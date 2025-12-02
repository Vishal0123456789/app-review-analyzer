"""
Layer 4: Email Pulse Sender
Generate and send weekly product pulse emails using Gemini LLM
"""

import json
import logging
import smtplib
import os
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Dict
import google.generativeai as genai

from .email_config import (
    INPUT_PULSE_FILE, OUTPUT_LOG_TEMPLATE, PRODUCT_NAME, PRODUCT_CONTEXT,
    FROM_EMAIL, TO_EMAILS, BCC_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USE_TLS,
    USE_MOCK_SEND, GEMINI_MODEL, SUBJECT_PROMPT_TEMPLATE, EMAIL_BODY_PROMPT_TEMPLATE,
    LOG_FILE, LOG_LEVEL
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmailPulseSender:
    """Generate and send weekly product pulse emails"""
    
    def __init__(self, api_key: str = None, pulse_file: str = None):
        """Initialize with optional Gemini API key and pulse file path"""
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
        else:
            self.model = None
        self.pulse_file = pulse_file or INPUT_PULSE_FILE
        logger.info(f"EmailPulseSender initialized with pulse file: {self.pulse_file}")
    
    def load_pulse_json(self) -> Dict:
        """Load the weekly pulse JSON from Layer 3"""
        logger.info(f"Loading pulse JSON from {self.pulse_file}")
        with open(self.pulse_file, 'r', encoding='utf-8') as f:
            pulse_data = json.load(f)
        logger.info(f"Loaded pulse data for {pulse_data.get('start_date')} to {pulse_data.get('end_date')}")
        return pulse_data
    
    def generate_subject_line(self, pulse_data: Dict) -> str:
        """Generate email subject line using LLM"""
        logger.info("Generating subject line...")
        
        start_date = pulse_data.get('start_date')
        end_date = pulse_data.get('end_date')
        
        prompt = SUBJECT_PROMPT_TEMPLATE.format(
            product_name=PRODUCT_NAME,
            start_date=start_date,
            end_date=end_date
        )
        
        try:
            response = self.model.generate_content(prompt)
            subject_line = response.text.strip()
            logger.info(f"Generated subject: {subject_line}")
            return subject_line
        except Exception as e:
            logger.error(f"Error generating subject line: {e}")
            # Fallback subject
            subject_line = f"Weekly Product Pulse – {PRODUCT_NAME} ({start_date}–{end_date})"
            logger.info(f"Using fallback subject: {subject_line}")
            return subject_line
    
    def generate_email_body(self, pulse_data: Dict) -> str:
        """Generate email body using LLM"""
        logger.info("Generating email body...")
        
        start_date = pulse_data.get('start_date')
        end_date = pulse_data.get('end_date')
        pulse_json = json.dumps(pulse_data, indent=2)
        
        prompt = EMAIL_BODY_PROMPT_TEMPLATE.format(
            pulse_json=pulse_json,
            product_name=PRODUCT_NAME,
            start_date=start_date,
            end_date=end_date
        )
        
        try:
            response = self.model.generate_content(prompt)
            email_body = response.text.strip()
            logger.info(f"Generated email body ({len(email_body)} characters)")
            return email_body
        except Exception as e:
            logger.error(f"Error generating email body: {e}")
            # Fallback body
            email_body = self._generate_fallback_email_body(pulse_data)
            return email_body
    
    def _generate_fallback_email_body(self, pulse_data: Dict) -> str:
        """Generate a fallback email body if LLM fails"""
        start_date = pulse_data.get('start_date')
        end_date = pulse_data.get('end_date')
        
        body = f"""Hi Team,

Here's the weekly product pulse for {PRODUCT_NAME} from {start_date} to {end_date}.

Weekly App Review Pulse

Overview:
• {len(pulse_data.get('quotes', []))} key user quotes captured this week
• {len(pulse_data.get('action_ideas', []))} priority action items identified
• {len(pulse_data.get('top_themes', []))} top themes driving user feedback

Top Themes:
"""
        for theme in pulse_data.get('top_themes', []):
            body += f"• {theme['theme']}\n"
        
        body += "\nUser Voice (Quotes):\n"
        for quote in pulse_data.get('quotes', []):
            body += f"• \"{quote}\"\n"
        
        body += "\nAction Ideas:\n"
        for idea in pulse_data.get('action_ideas', []):
            body += f"• {idea}\n"
        
        body += f"\nPlease see the detailed pulse note in the attached JSON for full context.\n\nBest regards,\nProduct Team"
        
        return body
    
    def send_email(self, subject: str, body: str, to_emails: list) -> Tuple[bool, str]:
        """Send email using SMTP or mock if enabled"""
        logger.info(f"Preparing to send email to {len(to_emails)} recipients")
        
        if USE_MOCK_SEND:
            logger.info("Using MOCK send (not actually sending)")
            return True, "mock_send"
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = FROM_EMAIL
            msg['To'] = ', '.join(to_emails)
            if BCC_EMAIL:
                msg['Bcc'] = BCC_EMAIL
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send via SMTP
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not smtp_username or not smtp_password:
                logger.error("SMTP credentials not set in environment variables")
                return False, "Missing SMTP credentials"
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if SMTP_USE_TLS:
                    server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return True, "sent"
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False, str(e)
    
    def save_send_log(self, pulse_data: Dict, subject: str, status: bool, error_msg: str = None) -> str:
        """Save email send status to log file"""
        week_start = pulse_data.get('start_date')
        week_end = pulse_data.get('end_date')
        
        # Format dates without hyphens
        week_start_fmt = week_start.replace('-', '') if week_start else ''
        week_end_fmt = week_end.replace('-', '') if week_end else ''
        
        log_file = OUTPUT_LOG_TEMPLATE.format(week_start=week_start_fmt, week_end=week_end_fmt)
        
        log_entry = {
            "week_start_date": week_start,
            "week_end_date": week_end,
            "product_name": PRODUCT_NAME,
            "to": TO_EMAILS,
            "from": FROM_EMAIL,
            "subject": subject,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "success" if status else "error",
            "error_message": error_msg if error_msg else None
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Email send log saved to {log_file}")
        return log_file
    
    def run(self, api_key: str = None) -> Tuple[str, str, str, str]:
        """Execute complete email generation and send pipeline"""
        logger.info("=" * 80)
        logger.info("Starting Weekly Email Pulse Generation and Send")
        logger.info("=" * 80)
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        if not self.model:
            logger.error("Gemini API not configured. Set GEMINI_API_KEY environment variable.")
            return None, None, None, None
        
        # Load pulse data
        pulse_data = self.load_pulse_json()
        
        # Generate subject line
        subject_line = self.generate_subject_line(pulse_data)
        
        # Generate email body
        email_body = self.generate_email_body(pulse_data)
        
        # Send email
        success, send_status = self.send_email(subject_line, email_body, TO_EMAILS)
        
        # Save log
        log_file = self.save_send_log(pulse_data, subject_line, success, send_status if not success else None)
        
        logger.info("\n" + "=" * 80)
        logger.info("EMAIL PULSE GENERATION COMPLETED")
        logger.info("=" * 80)
        logger.info(f"Subject: {subject_line}")
        logger.info(f"Recipients: {', '.join(TO_EMAILS)}")
        logger.info(f"Status: {'SUCCESS' if success else 'FAILED'}")
        logger.info(f"Log file: {log_file}")
        
        return subject_line, email_body, log_file, send_status


def main():
    """Main entry point"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not set. Email generation may fail.")
    
    sender = EmailPulseSender(api_key=api_key)
    subject, body, log_file, status = sender.run(api_key)
    
    if subject and body:
        print("\nWeekly Email Pulse Generated Successfully!")
        print(f"  Subject: {subject}")
        print(f"  Body length: {len(body)} characters")
        print(f"  Send log: {log_file}")
        print(f"  Status: {status}")
    else:
        print("Email pulse generation failed. Check logs for details.")


if __name__ == "__main__":
    main()
