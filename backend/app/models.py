from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base  # Changed to relative import
import enum

class TicketStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class TicketPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class TicketCategory(str, enum.Enum):
    NETWORK = "Network"
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    ACCESS = "Access"

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    priority = Column(String(20), nullable=False, default=TicketPriority.MEDIUM.value)
    status = Column(String(20), nullable=False, default=TicketStatus.OPEN.value)
    reporter_name = Column(String(100), nullable=False)
    assigned_to = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    activities = relationship("Activity", back_populates="ticket", cascade="all, delete-orphan")
    resolution = relationship("Resolution", back_populates="ticket", uselist=False, cascade="all, delete-orphan")

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="activities")

class Resolution(Base):
    __tablename__ = "resolutions"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, unique=True)
    root_cause = Column(Text, nullable=False)
    troubleshooting_steps = Column(Text, nullable=False)
    resolution_summary = Column(Text, nullable=False)
    prevention_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="resolution")

class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    problem = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)