import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./helpdesk.db')
    
    # Email settings
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'imap.gmail.com')
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 993))
    
    # Scheduler settings
    EMAIL_CHECK_INTERVAL = int(os.getenv('EMAIL_CHECK_INTERVAL', 5))  # minutes
    
    # Feature flags
    EMAIL_AUTO_TICKET_ENABLED = os.getenv('EMAIL_AUTO_TICKET_ENABLED', 'true').lower() == 'true'
    EMAIL_DEDUPLICATION_ENABLED = os.getenv('EMAIL_DEDUPLICATION_ENABLED', 'true').lower() == 'true'
    
    # Ticket defaults
    DEFAULT_TICKET_PRIORITY = os.getenv('DEFAULT_TICKET_PRIORITY', 'Medium')
    DEFAULT_TICKET_CATEGORY = os.getenv('DEFAULT_TICKET_CATEGORY', 'Network')
    
    @staticmethod
    def validate():
        """Validate critical settings"""
        if Settings.EMAIL_AUTO_TICKET_ENABLED:
            if not Settings.EMAIL_USERNAME or not Settings.EMAIL_PASSWORD:
                raise ValueError("EMAIL_USERNAME and EMAIL_PASSWORD must be set when EMAIL_AUTO_TICKET_ENABLED is true")