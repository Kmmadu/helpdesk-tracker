from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Activity
from ..schemas import Activity as ActivitySchema

router = APIRouter()

@router.get("/ticket/{ticket_id}", response_model=list[ActivitySchema])
def get_ticket_activities(ticket_id: int, db: Session = Depends(get_db)):
    activities = db.query(Activity).filter(Activity.ticket_id == ticket_id).order_by(Activity.timestamp.desc()).all()
    return activities