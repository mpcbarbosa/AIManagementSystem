from fastapi import FastAPI

from app.config import settings
from app.database import engine

app = FastAPI(title="AI Management System", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "healthy"}