from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Helpdesk API is running!"}

@app.get("/test")
def test():
    return {"status": "ok", "message": "Vercel deployment working!"}
