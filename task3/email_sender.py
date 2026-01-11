"""
Email Automation System
-----------------------
Sends bulk emails with personalization (name, subject)
Features:
- Secure SMTP authentication with TLS
- CSV-based recipient management
- Comprehensive logging
- Failed delivery handling with retry mechanism
"""

# Load environment variables from .env file
import config

import csv
import smtplib
import logging
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

log_filename = LOG_DIR / f"email_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """SMTP Configuration settings"""
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    sender_name: str = "Email Automation System"
    use_tls: bool = True
    
    @classmethod
    def from_env(cls) -> 'EmailConfig':
        """Load configuration from environment variables"""
        return cls(
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            sender_email=os.getenv('SENDER_EMAIL', ''),
            sender_password=os.getenv('SENDER_PASSWORD', ''),
            sender_name=os.getenv('SENDER_NAME', 'Email Automation System'),
            use_tls=os.getenv('USE_TLS', 'true').lower() == 'true'
        )


@dataclass
class EmailResult:
    """Result of an email send attempt"""
    recipient_email: str
    recipient_name: str
    success: bool
    error_message: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class EmailTemplate:
    """Email template with personalization support using $variable syntax"""
    
    def __init__(self, subject_template: str, body_template: str, is_html: bool = True):
        self.subject_template = subject_template
        self.body_template = body_template
        self.is_html = is_html
    
    def _safe_substitute(self, template: str, **kwargs) -> str:
        """Replace $variable placeholders with values (safe for CSS)"""
        result = template
        for key, value in kwargs.items():
            result = result.replace(f'${key}', str(value))
        return result
    
    def render(self, **kwargs) -> tuple[str, str]:
        """Render template with provided variables"""
        subject = self._safe_substitute(self.subject_template, **kwargs)
        body = self._safe_substitute(self.body_template, **kwargs)
        return subject, body
    
    @classmethod
    def from_file(cls, template_path: str) -> 'EmailTemplate':
        """Load template from HTML file"""
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract subject from template (first line starting with SUBJECT:)
        lines = content.split('\n')
        subject = ""
        body_start = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith('SUBJECT:'):
                subject = line.replace('SUBJECT:', '').strip()
                body_start = i + 1
                break
        
        body = '\n'.join(lines[body_start:])
        return cls(subject_template=subject, body_template=body, is_html=True)


class EmailAutomationSystem:
    """Main email automation system for bulk sending"""
    
    def __init__(self, config: EmailConfig, max_retries: int = 3, retry_delay: int = 5):
        self.config = config
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.results: List[EmailResult] = []
        self.failed_emails: List[Dict] = []
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create and return authenticated SMTP connection"""
        logger.info(f"Connecting to SMTP server: {self.config.smtp_server}:{self.config.smtp_port}")
        
        server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
        server.ehlo()
        
        if self.config.use_tls:
            server.starttls()
            server.ehlo()
            logger.info("TLS encryption enabled")
        
        server.login(self.config.sender_email, self.config.sender_password)
        logger.info("SMTP authentication successful")
        
        return server
    
    def _create_message(self, recipient_email: str, subject: str, body: str, is_html: bool = True) -> MIMEMultipart:
        """Create email message with proper headers"""
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{self.config.sender_name} <{self.config.sender_email}>"
        message['To'] = recipient_email
        
        if is_html:
            message.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            message.attach(MIMEText(body, 'plain', 'utf-8'))
        
        return message
    
    def send_single_email(self, server: smtplib.SMTP, recipient_email: str, 
                          recipient_name: str, subject: str, body: str, 
                          is_html: bool = True) -> EmailResult:
        """Send a single email with retry mechanism"""
        
        for attempt in range(1, self.max_retries + 1):
            try:
                message = self._create_message(recipient_email, subject, body, is_html)
                server.sendmail(
                    self.config.sender_email,
                    recipient_email,
                    message.as_string()
                )
                
                result = EmailResult(
                    recipient_email=recipient_email,
                    recipient_name=recipient_name,
                    success=True
                )
                logger.info(f"✓ Email sent successfully to {recipient_name} <{recipient_email}>")
                return result
                
            except smtplib.SMTPRecipientsRefused as e:
                error_msg = f"Recipient refused: {str(e)}"
                logger.warning(f"✗ Attempt {attempt}/{self.max_retries} failed for {recipient_email}: {error_msg}")
                
            except smtplib.SMTPDataError as e:
                error_msg = f"Data error: {str(e)}"
                logger.warning(f"✗ Attempt {attempt}/{self.max_retries} failed for {recipient_email}: {error_msg}")
                
            except smtplib.SMTPException as e:
                error_msg = f"SMTP error: {str(e)}"
                logger.warning(f"✗ Attempt {attempt}/{self.max_retries} failed for {recipient_email}: {error_msg}")
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.warning(f"✗ Attempt {attempt}/{self.max_retries} failed for {recipient_email}: {error_msg}")
            
            if attempt < self.max_retries:
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        # All retries exhausted
        result = EmailResult(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            success=False,
            error_message=error_msg
        )
        self.failed_emails.append({
            'email': recipient_email,
            'name': recipient_name,
            'error': error_msg
        })
        logger.error(f"✗ Failed to send email to {recipient_name} <{recipient_email}> after {self.max_retries} attempts")
        return result
    
    def load_recipients_from_csv(self, csv_path: str) -> List[Dict]:
        """Load recipient list from CSV file"""
        recipients = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                recipients.append(row)
        
        logger.info(f"Loaded {len(recipients)} recipients from {csv_path}")
        return recipients
    
    def send_bulk_emails(self, recipients: List[Dict], template: EmailTemplate, 
                         delay_between_emails: float = 1.0) -> List[EmailResult]:
        """Send bulk emails to all recipients with personalization"""
        
        logger.info(f"Starting bulk email send to {len(recipients)} recipients")
        self.results = []
        self.failed_emails = []
        
        try:
            server = self._create_smtp_connection()
            
            for i, recipient in enumerate(recipients, 1):
                logger.info(f"Processing recipient {i}/{len(recipients)}: {recipient.get('email', 'N/A')}")
                
                # Prepare personalization data
                personalization = {
                    'name': recipient.get('name', 'Valued Customer'),
                    'email': recipient.get('email', ''),
                    'first_name': recipient.get('name', 'Valued Customer').split()[0] if recipient.get('name') else 'Valued Customer',
                    **{k: v for k, v in recipient.items() if k not in ['name', 'email']}
                }
                
                # Use custom subject if provided in CSV, otherwise use template
                if 'subject' in recipient and recipient['subject']:
                    subject = template._safe_substitute(recipient['subject'], **personalization)
                    body = template._safe_substitute(template.body_template, **personalization)
                else:
                    subject, body = template.render(**personalization)
                
                result = self.send_single_email(
                    server=server,
                    recipient_email=recipient['email'],
                    recipient_name=recipient.get('name', 'Unknown'),
                    subject=subject,
                    body=body,
                    is_html=template.is_html
                )
                self.results.append(result)
                
                # Delay between emails to avoid rate limiting
                if i < len(recipients):
                    time.sleep(delay_between_emails)
            
            server.quit()
            logger.info("SMTP connection closed")
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during bulk send: {str(e)}")
            raise
        
        self._generate_summary()
        return self.results
    
    def _generate_summary(self):
        """Generate and log summary of email sending operation"""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        
        logger.info("=" * 50)
        logger.info("EMAIL SENDING SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total emails processed: {total}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {(successful/total*100):.1f}%" if total > 0 else "N/A")
        logger.info("=" * 50)
        
        if self.failed_emails:
            logger.info("Failed deliveries:")
            for fe in self.failed_emails:
                logger.info(f"  - {fe['name']} <{fe['email']}>: {fe['error']}")
    
    def export_results_to_csv(self, output_path: str = "email_results.csv"):
        """Export sending results to CSV file"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'recipient_email', 'recipient_name', 'success', 'error_message'])
            writer.writeheader()
            
            for result in self.results:
                writer.writerow({
                    'timestamp': result.timestamp,
                    'recipient_email': result.recipient_email,
                    'recipient_name': result.recipient_name,
                    'success': result.success,
                    'error_message': result.error_message or ''
                })
        
        logger.info(f"Results exported to {output_path}")
    
    def export_failed_to_csv(self, output_path: str = "failed_emails.csv"):
        """Export failed emails to CSV for retry"""
        if not self.failed_emails:
            logger.info("No failed emails to export")
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'email', 'error'])
            writer.writeheader()
            writer.writerows(self.failed_emails)
        
        logger.info(f"Failed emails exported to {output_path}")


def main():
    """Main entry point for the email automation system"""
    
    # Load configuration from environment variables
    config = EmailConfig.from_env()
    
    # Validate configuration
    if not config.sender_email or not config.sender_password:
        logger.error("Missing required environment variables: SENDER_EMAIL and SENDER_PASSWORD")
        logger.info("Please set the following environment variables:")
        logger.info("  export SENDER_EMAIL='your-email@gmail.com'")
        logger.info("  export SENDER_PASSWORD='your-app-password'")
        logger.info("  export SMTP_SERVER='smtp.gmail.com'  # Optional, defaults to Gmail")
        logger.info("  export SMTP_PORT='587'  # Optional, defaults to 587")
        return
    
    # Initialize the email automation system
    system = EmailAutomationSystem(config, max_retries=3, retry_delay=5)
    
    # Load template
    template_path = "email_template.html"
    if not os.path.exists(template_path):
        logger.error(f"Template file not found: {template_path}")
        return
    
    template = EmailTemplate.from_file(template_path)
    
    # Load recipients
    csv_path = "recipients.csv"
    if not os.path.exists(csv_path):
        logger.error(f"Recipients file not found: {csv_path}")
        return
    
    recipients = system.load_recipients_from_csv(csv_path)
    
    if not recipients:
        logger.warning("No recipients found in CSV file")
        return
    
    # Send emails
    try:
        system.send_bulk_emails(recipients, template, delay_between_emails=1.0)
        
        # Export results
        system.export_results_to_csv("logs/email_results.csv")
        system.export_failed_to_csv("logs/failed_emails.csv")
        
    except smtplib.SMTPAuthenticationError:
        logger.error("Authentication failed. If using Gmail, make sure to:")
        logger.error("1. Enable 2-Factor Authentication")
        logger.error("2. Generate an App Password: https://myaccount.google.com/apppasswords")
        logger.error("3. Use the App Password as SENDER_PASSWORD")
    except Exception as e:
        logger.error(f"Failed to complete email sending: {str(e)}")


if __name__ == "__main__":
    main()
