from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from .routes import tickets, activities, knowledge, dashboard, settings

from .database import engine, Base, get_db
from .routes import tickets, activities, knowledge, dashboard
from .services.email_processor import EmailScheduler
from .models import EmailLog
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Email scheduler instance
email_scheduler = EmailScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Helpdesk Ticketing System...")
    
    # Start email scheduler
    try:
        email_scheduler.start()
        logger.info("Email scheduler initialized")
    except Exception as e:
        logger.error(f"Failed to start email scheduler: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    email_scheduler.stop()
    logger.info("Email scheduler stopped")

app = FastAPI(
    title="Helpdesk Ticketing System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(activities.router, prefix="/api/activities", tags=["activities"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(settings.router, prefix="/api", tags=["settings"])

@app.get("/api/debug/routes")
def debug_routes():
    """Debug endpoint to see all registered routes"""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "methods": list(route.methods) if hasattr(route, 'methods') else [],
            "name": route.name if hasattr(route, 'name') else None
        })
    return {
        "total_routes": len(routes),
        "routes": routes
    }

@app.get("/")
def root():
    return {"message": "Helpdesk Ticketing System API"}

# Optional: Add a manual trigger endpoint for testing
@app.post("/api/email/process")
def process_emails_now():
    """Manually trigger email processing (for testing purposes)"""
    try:
        email_scheduler.process_emails_now()
        return {"message": "Email processing triggered"}
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/api/email/stats")
def get_email_stats(db: Session = Depends(get_db)):
    """Get email processing statistics"""
    total = db.query(EmailLog).count()
    today = db.query(EmailLog).filter(
        EmailLog.processed_at >= datetime.now() - timedelta(days=1)
    ).count()
    failed = db.query(EmailLog).filter(
        EmailLog.status == 'failed'
    ).count()
    
    success_rate = ((total - failed) / total * 100) if total > 0 else 0
    
    # Get last processed time
    last = db.query(EmailLog).order_by(EmailLog.processed_at.desc()).first()
    
    return {
        'total_processed': total,
        'today': today,
        'failed': failed,
        'success_rate': round(success_rate, 2),
        'last_processed': last.processed_at if last else None
    }