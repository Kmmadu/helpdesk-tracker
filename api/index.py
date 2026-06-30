from fastapi import FastAPI

# Create a new FastAPI app
app = FastAPI(title="Helpdesk API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Helpdesk API is running!", "status": "ok"}

@app.get("/test")
def test():
    return {"status": "ok", "message": "Vercel deployment is working!"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "helpdesk-tracker"}
