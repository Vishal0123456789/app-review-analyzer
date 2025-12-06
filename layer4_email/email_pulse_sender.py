"""
Layer 4: Email Pulse Sender
Generate and send weekly product pulse emails using Gemini LLM
"""

import json
import logging
import smtplib
import os
import re
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
            email_body = self._generate_fallback_email_body(pulse_data)
            return email_body
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """Convert Markdown text to HTML email dashboard format with premium styling"""
        # Extract greeting and date range from content
        lines = markdown_text.split('\n')
        greeting = ""
        date_range = ""
        
        # Find greeting and extract date range from subject-like content
        for idx, line in enumerate(lines[:10]):
            if line.startswith('Hi '):
                greeting = line
            if ' to ' in line and '2025' in line:
                date_range = line.strip()
        
        html_body = self._render_premium_header(greeting, date_range)
        
        # Parse content sections
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Process summary table (Key Insights Dashboard)
            if '|' in line and 'Theme' in line:
                table_lines = [line]
                i += 1
                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i])
                    i += 1
                html_body += self._render_key_insights_dashboard(table_lines)
                continue
            
            # Process theme sections (### headers)
            if line.startswith('### '):
                theme_name = line.replace('### ', '').strip()
                theme_content = ""
                i += 1
                
                while i < len(lines) and not lines[i].startswith('###') and not lines[i].startswith('##'):
                    if lines[i].strip():
                        theme_content += lines[i] + "\n"
                    i += 1
                
                html_body += self._render_premium_theme_card(theme_name, theme_content)
                continue
            
            # Process recommended action items
            if 'Recommended Action Items' in line or 'Action Roadmap' in line:
                action_content = ""
                i += 1
                
                while i < len(lines) and lines[i].strip() and not lines[i].startswith('##'):
                    if lines[i].strip():
                        action_content += lines[i] + "\n"
                    i += 1
                
                html_body += self._render_premium_action_section(action_content)
                continue
            
            # Process closing question
            if '?' in line and ('What would' in line or 'How will' in line or 'What will' in line):
                html_body += f'<div style="margin-top: 40px; padding-top: 25px; border-top: 3px solid #1e40af;"><p style="font-size: 16px; font-weight: 700; color: #1e40af; margin: 15px 0;">{line.strip()}</p></div>'
                i += 1
                continue
            
            i += 1
        
        # Wrap in full HTML email template
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4;">
    <div style="max-width: 900px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        {html_body}
    </div>
</body>
</html>"""
        
        return html_template
    
    def _render_premium_header(self, greeting: str, date_range: str) -> str:
        """Render premium full-width header with deep accent color"""
        header_html = f'''<div style="background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); padding: 40px 30px; color: #ffffff;">
            <h2 style="margin: 0 0 10px 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">Weekly Product Pulse</h2>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #e0e7ff; letter-spacing: 0.5px;">{date_range if date_range else 'Weekly Analysis'}</p>
        </div>
        <div style="padding: 30px;">'''
        
        return header_html
    
    def _render_key_insights_dashboard(self, table_lines: list) -> str:
        """Render Key Insights Dashboard with color-coded insight cards"""
        if len(table_lines) < 2:
            return ""
        
        # Parse table
        header = [h.strip() for h in table_lines[0].split('|')[1:-1]]
        rows = []
        for line in table_lines[2:]:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells:
                rows.append(cells)
        
        dashboard_html = '''<div style="margin: 30px 0 40px 0;">
            <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #1e40af;">Key Insights Dashboard</h3>
            <div style="display: grid; gap: 16px;">'''
        
        # Define color mapping for priority signals
        color_map = {
            'CRITICAL': '#dc2626',
            'HIGH': '#ea580c',
            'FOCUS': '#ca8a04'
        }
        
        for row in rows:
            if len(row) >= 3:
                theme = row[0]
                sentiment = row[1] if len(row) > 1 else ""
                priority = row[2] if len(row) > 2 else ""
                
                # Determine card color based on priority
                priority_color = '#0f172a'
                priority_bg = '#f0f9ff'
                badge_color = '#1e40af'
                
                for key, color in color_map.items():
                    if key in priority:
                        priority_color = color
                        badge_color = color
                        if key == 'CRITICAL':
                            priority_bg = '#fee2e2'
                        elif key == 'HIGH':
                            priority_bg = '#fed7aa'
                        elif key == 'FOCUS':
                            priority_bg = '#fef3c7'
                        break
                
                dashboard_html += f'''<div style="background-color: {priority_bg}; border-left: 4px solid {priority_color}; padding: 16px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0 0 6px 0; font-size: 15px; font-weight: 700; color: #0f172a;">{theme}</h4>
                            <p style="margin: 0; font-size: 13px; color: #555;">{sentiment}</p>
                        </div>
                        <span style="background-color: {badge_color}; color: #ffffff; padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: 600;">{priority}</span>
                    </div>
                </div>'''
        
        dashboard_html += '</div></div>'
        return dashboard_html
    
    def _render_premium_theme_card(self, theme_name: str, content: str) -> str:
        """Render theme section as a premium card with visual accents"""
        processed_content = ""
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Bold text
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #0f172a; font-weight: 700;">\1</strong>', line)
            
            # Blockquotes (user quotes)
            if line.startswith('>'):
                quote_text = line[1:].strip()
                processed_content += f'<blockquote style="border-left: 4px solid #1e40af; margin: 12px 0; padding: 12px 16px; background-color: #f0f9ff; border-radius: 4px; color: #1f2937; font-style: italic; font-size: 13px; line-height: 1.6;">"{quote_text}"</blockquote>'
            # Bullet points with icon support
            elif line.startswith('•'):
                bullet_text = line[1:].strip()
                # Determine icon based on content
                icon = '📌'
                if 'crash' in bullet_text.lower() or 'error' in bullet_text.lower() or 'bug' in bullet_text.lower():
                    icon = '❌'
                elif 'feature' in bullet_text.lower() or 'ui' in bullet_text.lower():
                    icon = '⚙️'
                elif 'performance' in bullet_text.lower() or 'speed' in bullet_text.lower():
                    icon = '⚡'
                elif 'user' in bullet_text.lower() or 'experience' in bullet_text.lower():
                    icon = '👤'
                
                processed_content += f'<div style="display: flex; margin: 10px 0; padding: 8px 0;">{icon} <span style="margin-left: 10px; color: #333; line-height: 1.5;">{bullet_text}</span></div>'
            else:
                processed_content += f'<p style="margin: 10px 0; color: #555; line-height: 1.6; font-size: 14px;">{line}</p>'
        
        # Extract theme number if present
        theme_label = theme_name
        theme_num = ''
        if theme_name[0].isdigit():
            parts = theme_name.split('.', 1)
            if len(parts) > 1:
                theme_num = parts[0]
                theme_label = parts[1].strip()
        
        card_html = f'''<div style="background-color: #f4f4f4; border-left: 5px solid #1e40af; border-radius: 6px; padding: 24px; margin: 20px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <h3 style="margin: 0 0 16px 0; font-size: 16px; font-weight: 700; color: #0f172a; padding-bottom: 8px; border-bottom: 2px solid #1e40af;">{theme_label}</h3>
            <div style="color: #333;">{processed_content}</div>
        </div>'''
        
        return card_html
    
    def _render_premium_action_section(self, content: str) -> str:
        """Render action items as a prioritized roadmap list with icons and badges"""
        actions_html = '''<div style="margin: 40px 0;">
            <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #1e40af;">Recommended Action Items</h3>
            <div style="display: grid; gap: 14px;">'''
        
        action_num = 1
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Bold text
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #0f172a; font-weight: 700;">\1</strong>', line)
            
            if line.startswith('•'):
                action_text = line[1:].strip()
                
                # Extract target timeline if present
                target_match = re.search(r'(Next \d+ Sprint[s]?|Within \d+ week[s]?|\d+ sprint[s]?)', action_text, re.IGNORECASE)
                target_timeline = target_match.group(1) if target_match else None
                
                # Remove target from text if found
                if target_timeline:
                    action_text = re.sub(r'\s*-?\s*' + re.escape(target_timeline), '', action_text).strip()
                
                actions_html += f'''<div style="background-color: #f0f9ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 16px; display: flex; align-items: flex-start;">
                    <div style="flex-shrink: 0; margin-right: 14px;">
                        <div style="background-color: #1e40af; color: #ffffff; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px;">{action_num}</div>
                    </div>
                    <div style="flex-grow: 1;">
                        <p style="margin: 0 0 8px 0; font-size: 14px; color: #0f172a; font-weight: 600;">{action_text}</p>'''
                
                if target_timeline:
                    actions_html += f'''<span style="background-color: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 3px; font-size: 12px; font-weight: 600;">{target_timeline}</span>'''
                
                actions_html += '</div></div>'
                action_num += 1
            elif '.' in line and not line.startswith('http'):
                # Regular numbered action item
                actions_html += f'''<div style="background-color: #f0f9ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 16px;">
                    <p style="margin: 0; font-size: 14px; color: #333; line-height: 1.6;">{line}</p>
                </div>'''
        
        actions_html += '</div></div>'
        return actions_html

    
    def _generate_fallback_email_body(self, pulse_data: Dict) -> str:
        """Generate a fallback email body if LLM fails"""
        start_date = pulse_data.get('start_date')
        end_date = pulse_data.get('end_date')
        
        body = f"""Hi Team,

Here's the weekly product pulse for {PRODUCT_NAME} from {start_date} to {end_date}.

Overview:
• {len(pulse_data.get('quotes', []))} key user quotes captured
• {len(pulse_data.get('action_ideas', []))} action items identified
• {len(pulse_data.get('top_themes', []))} top themes identified

Best regards,
Product Team"""
        
        return body
    
    def send_email(self, subject: str, body: str, to_emails: list) -> Tuple[bool, str]:
        """Send email using SMTP with HTML format"""
        logger.info(f"Preparing to send email to {len(to_emails)} recipients")
        logger.info(f"Email recipients: {to_emails}")
        
        if USE_MOCK_SEND:
            logger.info("Using MOCK send (not actually sending)")
            return True, "mock_send"
        
        try:
            # Convert Markdown body to HTML
            html_body = self.markdown_to_html(body)
            
            # Create message with both plain text and HTML alternatives
            msg = MIMEMultipart('alternative')
            msg['From'] = FROM_EMAIL
            msg['To'] = ', '.join(to_emails)
            if BCC_EMAIL:
                msg['Bcc'] = BCC_EMAIL
            msg['Subject'] = subject
            
            # Attach plain text version
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Attach HTML version (preferred)
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Send via SMTP
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            logger.info(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
            logger.info(f"SMTP Username: {smtp_username if smtp_username else 'NOT SET'}")
            logger.info(f"SMTP Password: {'SET' if smtp_password else 'NOT SET'}")
            
            if not smtp_username or not smtp_password:
                logger.error("SMTP credentials not set in environment variables")
                logger.error(f"Available env vars: {list(os.environ.keys())}")
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
        
        # Ensure API key is available
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
        elif not self.model:
            env_api_key = os.getenv('GEMINI_API_KEY')
            if env_api_key:
                genai.configure(api_key=env_api_key)
                self.model = genai.GenerativeModel(GEMINI_MODEL)
                logger.info("Gemini API configured from environment variable")
            else:
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
