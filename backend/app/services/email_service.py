import imaplib
import email
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from .email_parser import EmailParser
from .priority_detector import PriorityDetector
from .category_detector import CategoryDetector
from .ticket_factory import TicketFactory
from app.models import EmailLog, Ticket

logger = logging.getLogger(__name__)

class EmailService:
    """Enterprise email-to-ticket service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.imap_server = None
        self.parser = EmailParser()
        self.ticket_factory = TicketFactory()
        self.priority_detector = PriorityDetector()
        self.category_detector = CategoryDetector()
        
        # Get email configuration from environment
        self.email_host = os.getenv('EMAIL_HOST', 'imap.gmail.com')
        self.email_username = os.getenv('EMAIL_USERNAME')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_port = int(os.getenv('EMAIL_PORT', 993))
        
        self._validate_config()
        self._connect()
    
    def _validate_config(self):
        """Validate email configuration"""
        if not self.email_username or not self.email_password:
            raise ValueError("EMAIL_USERNAME and EMAIL_PASSWORD must be set in environment")
    
    def _connect(self):
        """Connect to email server"""
        try:
            logger.info(f"Connecting to {self.email_host}:{self.email_port}")
            self.imap_server = imaplib.IMAP4_SSL(self.email_host, self.email_port)
            self.imap_server.login(self.email_username, self.email_password)
            self.imap_server.select('INBOX')
            logger.info("Connected to email server successfully")
        except Exception as e:
            logger.error(f"Failed to connect to email server: {e}")
            raise
    
    def _reconnect_if_needed(self):
        """Reconnect if connection is lost"""
        try:
            if self.imap_server:
                # Test connection
                self.imap_server.noop()
            else:
                self._connect()
        except Exception as e:
            logger.warning(f"Connection lost, reconnecting: {e}")
            try:
                self._connect()
            except Exception as reconnect_error:
                logger.error(f"Failed to reconnect: {reconnect_error}")
                raise
    
    def fetch_unread_emails(self) -> List[Dict]:
        """Fetch unread emails from inbox"""
        try:
            self._reconnect_if_needed()
            
            # Search for unread emails
            status, messages = self.imap_server.search(None, 'UNSEEN')
            if status != 'OK':
                logger.info("No unread emails found")
                return []
            
            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} unread emails")
            
            emails = []
            for email_id in email_ids:
                try:
                    # Fetch the email
                    status, msg_data = self.imap_server.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        logger.warning(f"Failed to fetch email {email_id}")
                        continue
                    
                    email_body = msg_data[0][1]
                    email_msg = email.message_from_bytes(email_body)
                    
                    # Extract email data
                    subject = self.parser.decode_subject(
                        email_msg.get('Subject', 'No Subject')
                    )
                    from_address = self.parser.extract_email_address(
                        email_msg.get('From', '')
                    )
                    message_id = email_msg.get('Message-ID', '')
                    body = self.parser.extract_body(email_msg)
                    
                    # Skip if no body content
                    if not body and not subject:
                        logger.warning(f"Email {email_id} has no content")
                        self._mark_as_processed(email_id)
                        continue
                    
                    # Check for duplicate
                    if self._is_duplicate(message_id, from_address, subject):
                        logger.info(f"Duplicate email detected: {message_id}")
                        self._mark_as_processed(email_id)
                        # Log duplicate
                        self._log_email_processing(
                            message_id, from_address, subject, 
                            'duplicate', None, None
                        )
                        continue
                    
                    emails.append({
                        'email_id': email_id,
                        'message_id': message_id,
                        'from_address': from_address,
                        'subject': subject,
                        'body': body,
                        'attachments': self.parser.extract_attachments(email_msg),
                        'raw_message': email_msg
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}")
                    self._mark_as_processed(email_id)
                    self._log_email_processing(
                        'unknown', 'unknown', 'unknown',
                        'failed', str(e), None
                    )
            
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def _is_duplicate(self, message_id: str, from_address: str, subject: str) -> bool:
        """Check if email is a duplicate"""
        if not message_id and not from_address:
            return False
            
        # Check by message_id
        if message_id:
            duplicate = self.db.query(EmailLog).filter(
                EmailLog.message_id == message_id
            ).first()
            if duplicate:
                return True
        
        # Check same sender + subject within 5 minutes
        recent_time = datetime.now() - timedelta(minutes=5)
        duplicate = self.db.query(Ticket).filter(
            Ticket.email_from == from_address,
            Ticket.email_subject == subject,
            Ticket.created_at >= recent_time
        ).first()
        if duplicate:
            return True
        
        return False
    
    def _mark_as_processed(self, email_id):
        """Mark email as processed (read)"""
        try:
            self._reconnect_if_needed()
            self.imap_server.store(email_id, '+FLAGS', '\\Seen')
        except Exception as e:
            logger.error(f"Error marking email as processed: {e}")
    
    def _log_email_processing(self, message_id, from_address, subject, 
                              status, error_msg, ticket_id):
        """Log email processing status"""
        try:
            email_log = EmailLog(
                message_id=message_id,
                from_address=from_address,
                subject=subject,
                status=status,
                error_message=error_msg,
                ticket_id=ticket_id,
                processed_at=datetime.now()
            )
            self.db.add(email_log)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging email: {e}")
            self.db.rollback()
    
    def process_emails(self) -> List[Dict]:
        """Main processing function - orchestrates email to ticket creation"""
        results = []
        emails = self.fetch_unread_emails()
        
        if not emails:
            return results
        
        for email_data in emails:
            try:
                # Combine subject and body for analysis
                full_text = f"{email_data['subject']} {email_data['body']}"
                
                # Detect priority and category
                priority = self.priority_detector.detect(full_text)
                category = self.category_detector.detect(full_text)
                
                # Prepare ticket data
                ticket_data = {
                    'title': email_data['subject'],
                    'description': email_data['body'] or "No content in email body",
                    'category': category,
                    'priority': priority,
                    'reporter_name': email_data['from_address'],
                    'assigned_to': None,
                    'email_message_id': email_data['message_id'],
                    'email_from': email_data['from_address'],
                    'email_subject': email_data['subject']
                }
                
                # Create ticket
                ticket = self.ticket_factory.create_from_email(
                    self.db, ticket_data
                )
                
                # Log successful processing
                self._log_email_processing(
                    email_data['message_id'],
                    email_data['from_address'],
                    email_data['subject'],
                    'processed',
                    None,
                    ticket.id
                )
                
                # Mark email as processed
                self._mark_as_processed(email_data['email_id'])
                
                results.append({
                    'ticket_id': ticket.id,
                    'title': ticket.title,
                    'status': 'success'
                })
                
                logger.info(f"✅ Created ticket #{ticket.id} from email: {ticket.title}")
                
            except Exception as e:
                logger.error(f"Error processing email: {e}")
                # Log error
                self._log_email_processing(
                    email_data.get('message_id', 'unknown'),
                    email_data.get('from_address', 'unknown'),
                    email_data.get('subject', 'unknown'),
                    'failed',
                    str(e),
                    None
                )
                
                results.append({
                    'error': str(e),
                    'status': 'error'
                })
        
        return results
    
    def disconnect(self):
        """Disconnect from email server"""
        try:
            if self.imap_server:
                self.imap_server.close()
                self.imap_server.logout()
                logger.info("Disconnected from email server")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")