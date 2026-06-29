from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from ..database import get_db
from ..models import Ticket, Activity, Resolution, User
from ..schemas import Ticket as TicketSchema, TicketCreate, TicketUpdate, ResolutionCreate
from ..auth import get_current_active_user, get_technician_user, get_admin_user

router = APIRouter()

def serialize_user(user):
    """Helper function to convert User object to dict"""
    if not user:
        return None
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email
    }

@router.post("/", response_model=TicketSchema)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Find assigned user if provided
    assigned_user_id = None
    if ticket.assigned_to:
        # Try to find user by username first, then email
        assigned_user = db.query(User).filter(User.username == ticket.assigned_to).first()
        if not assigned_user:
            assigned_user = db.query(User).filter(User.email == ticket.assigned_to).first()
        if assigned_user:
            assigned_user_id = assigned_user.id
    
    # Create ticket with current user as reporter
    db_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        reporter_id=current_user.id,
        assigned_to_id=assigned_user_id,  # Handle assignment
        source=ticket.source if hasattr(ticket, 'source') else "Manual",
        email_message_id=ticket.email_message_id if hasattr(ticket, 'email_message_id') else None,
        email_from=ticket.email_from if hasattr(ticket, 'email_from') else None,
        email_subject=ticket.email_subject if hasattr(ticket, 'email_subject') else None,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Create activity log - Ticket creation
    activity = Activity(
        ticket_id=db_ticket.id,
        action="Ticket Created",
        description=f"Ticket '{db_ticket.title}' was created by {current_user.full_name or current_user.username}"
    )
    db.add(activity)
    
    # Log assignment if assigned
    if assigned_user_id:
        assigned_user = db.query(User).filter(User.id == assigned_user_id).first()
        activity2 = Activity(
            ticket_id=db_ticket.id,
            action="Assigned",
            description=f"Assigned to {assigned_user.full_name or assigned_user.username}"
        )
        db.add(activity2)
    
    db.commit()
    
    # Refresh to load relationships
    db.refresh(db_ticket)
    
    # Convert to response format
    ticket_dict = {
        "id": db_ticket.id,
        "title": db_ticket.title,
        "description": db_ticket.description,
        "category": db_ticket.category,
        "priority": db_ticket.priority,
        "status": db_ticket.status,
        "created_at": db_ticket.created_at,
        "updated_at": db_ticket.updated_at,
        "source": db_ticket.source,
        "email_message_id": db_ticket.email_message_id,
        "email_from": db_ticket.email_from,
        "email_subject": db_ticket.email_subject,
        "processed_at": db_ticket.processed_at,
        "email_attachments": db_ticket.email_attachments,
        "reporter": serialize_user(current_user),
        "assigned_to": serialize_user(db_ticket.assigned_to)
    }
    
    return ticket_dict

@router.get("/", response_model=List[TicketSchema])
def get_tickets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Use joinedload to eager load relationships
    query = db.query(Ticket).options(
        joinedload(Ticket.reporter),
        joinedload(Ticket.assigned_to)
    )
    
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if search:
        query = query.filter(Ticket.title.contains(search))
    
    tickets = query.offset(skip).limit(limit).all()
    
    # Convert tickets to response format with user info
    result = []
    for ticket in tickets:
        ticket_dict = {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "source": ticket.source,
            "email_message_id": ticket.email_message_id,
            "email_from": ticket.email_from,
            "email_subject": ticket.email_subject,
            "processed_at": ticket.processed_at,
            "email_attachments": ticket.email_attachments,
            "reporter": serialize_user(ticket.reporter),
            "assigned_to": serialize_user(ticket.assigned_to)
        }
        result.append(ticket_dict)
    
    return result

@router.get("/{ticket_id}", response_model=TicketSchema)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    ticket = db.query(Ticket).options(
        joinedload(Ticket.reporter),
        joinedload(Ticket.assigned_to)
    ).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Convert to response format with user info
    ticket_dict = {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "source": ticket.source,
        "email_message_id": ticket.email_message_id,
        "email_from": ticket.email_from,
        "email_subject": ticket.email_subject,
        "processed_at": ticket.processed_at,
        "email_attachments": ticket.email_attachments,
        "reporter": serialize_user(ticket.reporter),
        "assigned_to": serialize_user(ticket.assigned_to)
    }
    
    return ticket_dict

@router.put("/{ticket_id}", response_model=TicketSchema)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    old_status = ticket.status
    old_assigned_id = ticket.assigned_to_id
    
    # Update fields - skip 'assigned_to' as we handle it separately
    update_data = ticket_update.model_dump(exclude_unset=True)
    
    # Handle assigned_to separately (convert username/email to user_id)
    assigned_to_value = None
    if 'assigned_to' in update_data:
        assigned_to_value = update_data.pop('assigned_to')  # Remove from update_data
    
    # Update all other fields
    for key, value in update_data.items():
        setattr(ticket, key, value)
    
    # Handle assignment if provided
    if assigned_to_value is not None:
        if assigned_to_value:
            # Try to find user by username first, then email
            assigned_user = db.query(User).filter(User.username == assigned_to_value).first()
            if not assigned_user:
                assigned_user = db.query(User).filter(User.email == assigned_to_value).first()
            
            if assigned_user:
                ticket.assigned_to_id = assigned_user.id
            else:
                # User not found, keep current assignment
                pass
        else:
            # Empty string or None means unassign
            ticket.assigned_to_id = None
    
    db.commit()
    db.refresh(ticket)
    
    # Log status changes
    if ticket_update.status and ticket_update.status != old_status:
        activity = Activity(
            ticket_id=ticket.id,
            action="Status Changed",
            description=f"Status changed from {old_status} to {ticket_update.status}"
        )
        db.add(activity)
    
    # Log assignment changes
    if ticket.assigned_to_id != old_assigned_id:
        if ticket.assigned_to_id:
            assigned_user = db.query(User).filter(User.id == ticket.assigned_to_id).first()
            activity = Activity(
                ticket_id=ticket.id,
                action="Assigned",
                description=f"Assigned to {assigned_user.full_name or assigned_user.username if assigned_user else 'Unknown'}"
            )
        else:
            activity = Activity(
                ticket_id=ticket.id,
                action="Unassigned",
                description="Ticket unassigned"
            )
        db.add(activity)
    
    db.commit()
    
    # Refresh to load relationships
    db.refresh(ticket)
    
    # Convert to response format with user info
    ticket_dict = {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "source": ticket.source,
        "email_message_id": ticket.email_message_id,
        "email_from": ticket.email_from,
        "email_subject": ticket.email_subject,
        "processed_at": ticket.processed_at,
        "email_attachments": ticket.email_attachments,
        "reporter": serialize_user(ticket.reporter),
        "assigned_to": serialize_user(ticket.assigned_to)
    }
    
    return ticket_dict

@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Only admins can delete
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted successfully"}

@router.post("/{ticket_id}/resolve")
def resolve_ticket(
    ticket_id: int,
    resolution: ResolutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_technician_user)  # Technicians and admins can resolve
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket status
    ticket.status = "Resolved"
    
    # Create resolution record
    db_resolution = Resolution(**resolution.model_dump())
    db.add(db_resolution)
    
    # Log resolution
    activity = Activity(
        ticket_id=ticket.id,
        action="Ticket Resolved",
        description=f"Ticket resolved by {current_user.full_name or current_user.username} with summary: {resolution.resolution_summary[:100]}..."
    )
    db.add(activity)
    
    db.commit()
    
    return {"message": "Ticket resolved successfully"}