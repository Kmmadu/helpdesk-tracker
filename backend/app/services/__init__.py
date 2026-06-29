# This file makes the services directory a Python package
from .email_service import EmailService
from .email_parser import EmailParser
from .priority_detector import PriorityDetector
from .category_detector import CategoryDetector
from .ticket_factory import TicketFactory
from .email_processor import EmailScheduler

__all__ = [
    'EmailService',
    'EmailParser', 
    'PriorityDetector',
    'CategoryDetector',
    'TicketFactory',
    'EmailScheduler'
]