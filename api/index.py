from fastapi import FastAPI

# Create a simple, standalone FastAPI app
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

# Add a simple echo endpoint to test POST requests
@app.post("/api/echo")
def echo(data: dict):
    return {"received": data, "status": "ok"}
