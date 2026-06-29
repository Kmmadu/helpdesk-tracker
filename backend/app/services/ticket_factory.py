from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime
import logging
from app.models import Ticket, Activity

logger = logging.getLogger(__name__)

class TicketFactory:
    """Factory for creating tickets from various sources"""
    
    @staticmethod
    def create_from_email(db: Session, email_data: Dict) -> Ticket:
        """
        Create a ticket from email data
        
        Args:
            db: Database session
            email_data: Dictionary containing email data
            
        Returns:
            Created Ticket object
        """
        try:
            # Truncate title if too long (max 200 chars)
            title = email_data['title']
            if len(title) > 200:
                title = title[:197] + "..."
            
            # Create ticket
            ticket = Ticket(
                title=title,
                description=email_data['description'],
                category=email_data.get('category', 'Network'),
                priority=email_data.get('priority', 'Medium'),
                reporter_name=email_data['reporter_name'],
                assigned_to=email_data.get('assigned_to'),
                source='Email',
                email_message_id=email_data.get('email_message_id'),
                email_from=email_data.get('email_from'),
                email_subject=email_data.get('email_subject'),
                created_at=datetime.now()
            )
            
            db.add(ticket)
            db.flush()  # Get the ID without committing
            
            # Create activity log - Ticket creation
            activity1 = Activity(
                ticket_id=ticket.id,
                action="Ticket Created Automatically",
                description=f"Ticket created automatically from email from {ticket.reporter_name}"
            )
            db.add(activity1)
            
            # Create activity log - Email source
            activity2 = Activity(
                ticket_id=ticket.id,
                action="Email Received",
                description=f"Original email: {ticket.email_subject}"
            )
            db.add(activity2)
            
            # If there's a category, log it
            if email_data.get('category'):
                activity3 = Activity(
                    ticket_id=ticket.id,
                    action="Category Detected",
                    description=f"Auto-categorized as: {email_data['category']}"
                )
                db.add(activity3)
            
            # If there's a priority, log it
            if email_data.get('priority'):
                activity4 = Activity(
                    ticket_id=ticket.id,
                    action="Priority Detected",
                    description=f"Auto-priority set to: {email_data['priority']}"
                )
                db.add(activity4)
            
            db.commit()
            db.refresh(ticket)
            
            logger.info(f"Created ticket #{ticket.id} from email: {ticket.email_subject}")
            return ticket
            
        except Exception as e:
            logger.error(f"Error creating ticket from email: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def create_from_api(db: Session, ticket_data: Dict) -> Ticket:
        """
        Create a ticket from API data (for future use)
        """
        # Similar implementation for API-created tickets
        pass