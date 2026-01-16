from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas.customers import CustomerCreate, CustomerResponse, CustomerListResponse
from app.services.customers import (
    create_customer as create_customer_service,
    get_customer as get_customer_service,
    get_customers as get_customers_service,
    update_customer as update_customer_service,
    delete_customer as delete_customer_service,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return create_customer_service(db, customer)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    return get_customer_service(db, customer_id)


@router.get("/", response_model=CustomerListResponse)
async def get_customers(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return get_customers_service(db, limit, offset)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: UUID, customer: CustomerCreate, db: Session = Depends(get_db)):
    return update_customer_service(db, customer_id, customer)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: UUID, db: Session = Depends(get_db)):
    delete_customer_service(db, customer_id)
    return None