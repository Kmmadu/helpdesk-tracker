from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from ..models import Ticket, Activity, Resolution
from ..schemas import Ticket as TicketSchema, TicketCreate, TicketUpdate, ResolutionCreate

router = APIRouter()

@router.post("/", response_model=TicketSchema)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    db_ticket = Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Create activity log
    activity = Activity(
        ticket_id=db_ticket.id,
        action="Ticket Created",
        description=f"Ticket '{db_ticket.title}' was created by {db_ticket.reporter_name}"
    )
    db.add(activity)
    db.commit()
    
    return db_ticket

@router.get("/", response_model=List[TicketSchema])
def get_tickets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)
    
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if search:
        query = query.filter(Ticket.title.contains(search))
    
    return query.offset(skip).limit(limit).all()

@router.get("/{ticket_id}", response_model=TicketSchema)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}", response_model=TicketSchema)
def update_ticket(ticket_id: int, ticket_update: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    old_status = ticket.status
    old_assigned = ticket.assigned_to
    
    for key, value in ticket_update.model_dump(exclude_unset=True).items():
        setattr(ticket, key, value)
    
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
    if ticket_update.assigned_to is not None and ticket_update.assigned_to != old_assigned:
        activity = Activity(
            ticket_id=ticket.id,
            action="Assigned",
            description=f"Assigned to {ticket_update.assigned_to}"
        )
        db.add(activity)
    
    db.commit()
    return ticket

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted successfully"}

@router.post("/{ticket_id}/resolve")
def resolve_ticket(ticket_id: int, resolution: ResolutionCreate, db: Session = Depends(get_db)):
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
        description=f"Ticket resolved with summary: {resolution.resolution_summary[:100]}..."
    )
    db.add(activity)
    
    db.commit()
    return {"message": "Ticket resolved successfully"}