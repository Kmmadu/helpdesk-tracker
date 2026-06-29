from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict
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

class TicketSource(str, Enum):
    MANUAL = "Manual"
    EMAIL = "Email"
    API = "API"

# ============================================
# TICKET SCHEMAS - FIXED
# ============================================

class TicketBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    assigned_to: Optional[str] = None  # ADDED - allows assigning on creation

class TicketCreate(TicketBase):
    source: Optional[TicketSource] = TicketSource.MANUAL
    email_message_id: Optional[str] = None
    email_from: Optional[str] = None
    email_subject: Optional[str] = None
    # assigned_to is inherited from TicketBase

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
    source: TicketSource = TicketSource.MANUAL
    email_message_id: Optional[str] = None
    email_from: Optional[str] = None
    email_subject: Optional[str] = None
    processed_at: Optional[datetime] = None
    email_attachments: Optional[List[Dict]] = None
    
    # User relationships (return as dict with user info)
    reporter: Optional[dict] = None
    assigned_to: Optional[dict] = None
    
    class Config:
        from_attributes = True

# ============================================
# ACTIVITY SCHEMAS
# ============================================

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

# ============================================
# RESOLUTION SCHEMAS
# ============================================

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

# ============================================
# KNOWLEDGE ARTICLE SCHEMAS
# ============================================

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

# ============================================
# DASHBOARD SCHEMAS
# ============================================

class DashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    critical_tickets: int
    most_common_category: Optional[str]

# ============================================
# EMAIL LOG SCHEMAS
# ============================================

class EmailLogBase(BaseModel):
    message_id: str
    from_address: str
    subject: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    ticket_id: Optional[int] = None
    retry_count: int = 0

class EmailLogCreate(EmailLogBase):
    pass

class EmailLog(EmailLogBase):
    id: int
    processed_at: datetime
    
    class Config:
        from_attributes = True

class EmailStats(BaseModel):
    total_processed: int
    today: int
    failed: int
    success_rate: float
    last_processed: Optional[datetime]

# ============================================
# USER AUTHENTICATION SCHEMAS
# ============================================

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: str = "user"

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[dict] = None

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True