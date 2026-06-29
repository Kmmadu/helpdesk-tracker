from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum
from typing import Optional

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

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, default="user")  # admin, technician, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tickets_created = relationship("Ticket", foreign_keys="Ticket.reporter_id", back_populates="reporter")
    tickets_assigned = relationship("Ticket", foreign_keys="Ticket.assigned_to_id", back_populates="assigned_to")

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    priority = Column(String(20), nullable=False, default=TicketPriority.MEDIUM.value)
    status = Column(String(20), nullable=False, default=TicketStatus.OPEN.value)
    
    # User relationships (replaces reporter_name and assigned_to)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Email-specific fields (keep for backward compatibility)
    source = Column(String(20), nullable=False, default="Manual")
    email_message_id = Column(String(255), nullable=True, unique=True)
    email_from = Column(String(255), nullable=True)
    email_subject = Column(String(500), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    email_attachments = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="tickets_created")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="tickets_assigned")
    activities = relationship("Activity", back_populates="ticket", cascade="all, delete-orphan")
    resolution = relationship("Resolution", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_tickets_email_message_id', 'email_message_id'),
        Index('ix_tickets_source', 'source'),
        Index('ix_tickets_created_at', 'created_at'),
        Index('ix_tickets_status', 'status'),
        Index('ix_tickets_category', 'category'),
        Index('ix_tickets_priority', 'priority'),
        Index('ix_tickets_reporter_id', 'reporter_id'),
        Index('ix_tickets_assigned_to_id', 'assigned_to_id'),
    )

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

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), nullable=False)
    from_address = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    retry_count = Column(Integer, default=0)
    
    __table_args__ = (
        Index('ix_email_logs_message_id', 'message_id'),
        Index('ix_email_logs_status', 'status'),
        Index('ix_email_logs_processed_at', 'processed_at'),
    )
    
    # Relationship
    ticket = relationship("Ticket")

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_encrypted = Column(Boolean, default=False)