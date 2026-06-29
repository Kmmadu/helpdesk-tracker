import email
import re
from email.header import decode_header
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class EmailParser:
    """Parse emails and extract relevant information"""
    
    @staticmethod
    def decode_subject(subject: str) -> str:
        """Decode email subject if encoded"""
        if not subject:
            return "No Subject"
            
        try:
            decoded = []
            for part, encoding in decode_header(subject):
                if isinstance(part, bytes):
                    if encoding:
                        decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
                    else:
                        decoded.append(part.decode('utf-8', errors='ignore'))
                else:
                    decoded.append(part)
            return ' '.join(decoded)
        except Exception as e:
            logger.error(f"Error decoding subject: {e}")
            return subject or "No Subject"
    
    @staticmethod
    def extract_body(email_msg) -> str:
        """Extract plain text body from email"""
        body = ""
        
        try:
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    # Skip attachments
                    if "attachment" in content_disposition:
                        continue
                    
                    if content_type == "text/plain":
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='ignore')
                                break
                        except Exception as e:
                            logger.warning(f"Error decoding text/plain part: {e}")
                            continue
            else:
                try:
                    payload = email_msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                    else:
                        body = str(email_msg.get_payload())
                except Exception as e:
                    logger.warning(f"Error decoding email body: {e}")
                    body = str(email_msg.get_payload())
        except Exception as e:
            logger.error(f"Error extracting body: {e}")
            return ""
        
        # Clean up
        body = re.sub(r'\r\n', '\n', body)
        body = re.sub(r'\n{3,}', '\n\n', body)
        return body.strip()
    
    @staticmethod
    def extract_attachments(email_msg) -> List[Dict]:
        """Extract attachment metadata"""
        attachments = []
        
        try:
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            # Decode filename if needed
                            try:
                                filename = EmailParser.decode_subject(filename)
                            except:
                                pass
                            
                            attachments.append({
                                'filename': filename,
                                'content_type': part.get_content_type(),
                                'size': len(part.get_payload(decode=True) or b'')
                            })
        except Exception as e:
            logger.error(f"Error extracting attachments: {e}")
        
        return attachments
    
    @staticmethod
    def extract_email_address(text: str) -> str:
        """Extract email address from From field"""
        if not text:
            return ""
        
        try:
            # Simple extraction
            match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            if match:
                return match.group(0)
            return text
        except:
            return text