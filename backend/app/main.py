from fastapi import FastAPI

from app.api.customers import router as customers_router

app = FastAPI(title="AI Management System", version="1.0.0")

app.include_router(customers_router)


@app.get("/health")
def health():
    return {"status": "healthy"}
