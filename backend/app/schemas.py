from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class TicketCategory(str, Enum):
    NETWORK = "Network"
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    ACCESS = "Access"

# Ticket Schemas
class TicketBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    reporter_name: str = Field(..., max_length=100)
    assigned_to: Optional[str] = Field(None, max_length=100)

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_to: Optional[str] = Field(None, max_length=100)

class Ticket(TicketBase):
    id: int
    status: TicketStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Activity Schemas
class ActivityBase(BaseModel):
    ticket_id: int
    action: str = Field(..., max_length=100)
    description: str

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Resolution Schemas
class ResolutionBase(BaseModel):
    root_cause: str
    troubleshooting_steps: str
    resolution_summary: str
    prevention_notes: Optional[str] = None

class ResolutionCreate(ResolutionBase):
    ticket_id: int

class Resolution(ResolutionBase):
    id: int
    ticket_id: int
    resolved_at: datetime
    
    class Config:
        from_attributes = True

# Knowledge Article Schemas
class KnowledgeArticleBase(BaseModel):
    title: str = Field(..., max_length=200)
    problem: str
    solution: str
    category: TicketCategory

class KnowledgeArticleCreate(KnowledgeArticleBase):
    ticket_id: Optional[int] = None

class KnowledgeArticle(KnowledgeArticleBase):
    id: int
    created_date: datetime
    ticket_id: Optional[int]
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    critical_tickets: int
    most_common_category: Optional[str]