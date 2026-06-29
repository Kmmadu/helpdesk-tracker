from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
import os

from .email_service import EmailService
from app.database import SessionLocal

logger = logging.getLogger(__name__)

class EmailScheduler:
    """Background scheduler for processing emails"""
    
    _instance = None
    _scheduler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def start(self):
        """Start the email processing scheduler"""
        if self._scheduler:
            logger.info("Email scheduler already running")
            return
        
        # Check if email automation is enabled
        if not os.getenv('EMAIL_AUTO_TICKET_ENABLED', 'true').lower() == 'true':
            logger.info("Email automation is disabled via EMAIL_AUTO_TICKET_ENABLED")
            return
        
        # Check if email credentials are configured
        if not os.getenv('EMAIL_USERNAME') or not os.getenv('EMAIL_PASSWORD'):
            logger.warning("Email credentials not configured. Email automation disabled.")
            logger.info("Set EMAIL_USERNAME and EMAIL_PASSWORD in .env to enable")
            return
        
        self._scheduler = BackgroundScheduler()
        
        # Get interval from environment (default: 5 minutes)
        interval_minutes = int(os.getenv('EMAIL_CHECK_INTERVAL', 5))
        
        # Schedule the job
        self._scheduler.add_job(
            self._process_emails,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='email_processor',
            replace_existing=True,
            next_run_time=datetime.now()  # Run immediately on startup
        )
        
        self._scheduler.start()
        logger.info(f"✅ Email scheduler started - checking every {interval_minutes} minutes")
    
    def stop(self):
        """Stop the scheduler"""
        if self._scheduler:
            self._scheduler.shutdown()
            logger.info("Email scheduler stopped")
    
    @staticmethod
    def _process_emails():
        """Process emails in background"""
        db = None
        try:
            logger.info("🔄 Checking for new emails...")
            db = SessionLocal()
            email_service = EmailService(db)
            results = email_service.process_emails()
            
            if results:
                success_count = sum(1 for r in results if r.get('status') == 'success')
                error_count = len(results) - success_count
                
                if success_count > 0:
                    logger.info(f"✅ Processed {success_count} emails successfully")
                if error_count > 0:
                    logger.warning(f"❌ Failed to process {error_count} emails")
            else:
                logger.debug("📭 No new emails to process")
            
            email_service.disconnect()
            
        except Exception as e:
            logger.error(f"❌ Email processing error: {e}")
        finally:
            if db:
                db.close()
    
    @staticmethod
    def process_emails_now():
        """Manually trigger email processing (for testing)"""
        logger.info("Manual email processing triggered")
        EmailScheduler._process_emails()