from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database import get_db
from ..models import Setting
from datetime import datetime
import os

router = APIRouter()

@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    """Get all settings"""
    settings = db.query(Setting).all()
    return {s.key: s.value for s in settings}

@router.put("/settings/email")
def update_email_settings(
    settings_data: Dict[str, Any], 
    db: Session = Depends(get_db)
):
    """Update email settings"""
    allowed_keys = [
        'EMAIL_HOST', 
        'EMAIL_USERNAME', 
        'EMAIL_PASSWORD', 
        'EMAIL_PORT',
        'EMAIL_CHECK_INTERVAL',
        'EMAIL_AUTO_TICKET_ENABLED'
    ]
    
    for key, value in settings_data.items():
        if key not in allowed_keys:
            continue
            
        # Check if setting exists
        existing = db.query(Setting).filter(Setting.key == key).first()
        if existing:
            existing.value = str(value)
            existing.updated_at = datetime.now()
        else:
            db_setting = Setting(key=key, value=str(value))
            db.add(db_setting)
    
    db.commit()
    
    # Update environment variables for current session
    for key, value in settings_data.items():
        if key in allowed_keys:
            os.environ[key] = str(value)
    
    return {"message": "Settings updated successfully"}

@router.get("/settings/email/test")
def test_email_connection(db: Session = Depends(get_db)):
    """Test email connection with current settings"""
    # Get settings from database
    settings = db.query(Setting).all()
    settings_dict = {s.key: s.value for s in settings}
    
    # Check if all required settings exist
    required = ['EMAIL_HOST', 'EMAIL_USERNAME', 'EMAIL_PASSWORD']
    missing = [r for r in required if r not in settings_dict or not settings_dict[r]]
    
    if missing:
        return {"status": "error", "message": f"Missing settings: {', '.join(missing)}"}
    
    try:
        import imaplib
        server = imaplib.IMAP4_SSL(settings_dict['EMAIL_HOST'])
        server.login(settings_dict['EMAIL_USERNAME'], settings_dict['EMAIL_PASSWORD'])
        server.select('INBOX')
        server.close()
        server.logout()
        return {"status": "success", "message": "Email connection successful!"}
    except Exception as e:
        return {"status": "error", "message": f"Connection failed: {str(e)}"}
