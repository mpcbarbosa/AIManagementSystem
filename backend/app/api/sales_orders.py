from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas.sales_orders import SalesOrderCreate, SalesOrderResponse, SalesOrderListResponse
from app.services.sales_orders import (
    create_sales_order as create_sales_order_service,
    get_sales_order as get_sales_order_service,
    get_sales_orders as get_sales_orders_service,
    update_sales_order as update_sales_order_service,
    delete_sales_order as delete_sales_order_service,
)

router = APIRouter(prefix="/sales-orders", tags=["sales-orders"])


@router.post("/", response_model=SalesOrderResponse)
async def create_sales_order(order: SalesOrderCreate, db: Session = Depends(get_db)):
    return create_sales_order_service(db, order)


@router.get("/{order_id}", response_model=SalesOrderResponse)
async def get_sales_order(order_id: UUID, db: Session = Depends(get_db)):
    return get_sales_order_service(db, order_id)


@router.get("/", response_model=SalesOrderListResponse)
async def get_sales_orders(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return get_sales_orders_service(db, limit, offset)


@router.put("/{order_id}", response_model=SalesOrderResponse)
async def update_sales_order(order_id: UUID, order: SalesOrderCreate, db: Session = Depends(get_db)):
    return update_sales_order_service(db, order_id, order)


@router.delete("/{order_id}", status_code=204)
async def delete_sales_order(order_id: UUID, db: Session = Depends(get_db)):
    delete_sales_order_service(db, order_id)
    return None