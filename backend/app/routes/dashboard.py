from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Ticket
from ..schemas import DashboardStats

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == "Open").count()
    in_progress = db.query(Ticket).filter(Ticket.status == "In Progress").count()
    resolved = db.query(Ticket).filter(Ticket.status == "Resolved").count()
    critical = db.query(Ticket).filter(Ticket.priority == "Critical").count()
    
    # Most common category
    categories = db.query(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category).all()
    most_common = None
    if categories:
        most_common = max(categories, key=lambda x: x[1])[0] if categories else None
    
    return DashboardStats(
        total_tickets=total,
        open_tickets=open_tickets,
        in_progress_tickets=in_progress,
        resolved_tickets=resolved,
        critical_tickets=critical,
        most_common_category=most_common
    )