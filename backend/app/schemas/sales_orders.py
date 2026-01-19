from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import List


class SalesOrderItemCreate(BaseModel):
    item_id: UUID
    quantity: int = Field(gt=0)


class SalesOrderCreate(BaseModel):
    customer_id: UUID
    contact_id: UUID
    address_id: UUID
    items: List[SalesOrderItemCreate] = Field(min_length=1)

    @field_validator('items')
    @classmethod
    def validate_unique_items(cls, v):
        item_ids = [item.item_id for item in v]
        if len(item_ids) != len(set(item_ids)):
            raise ValueError('Duplicate items in order')
        return v


class SalesOrderItemResponse(BaseModel):
    item_id: UUID
    name: str
    price: float
    quantity: int
    unit_price: float
    line_total: float


class SalesOrderResponse(BaseModel):
    id: UUID
    customer_id: UUID
    contact_id: UUID
    address_id: UUID
    order_date: datetime
    status: str
    items: List[SalesOrderItemResponse]
    order_total: float
    created_at: datetime
    updated_at: datetime


class SalesOrderListResponse(BaseModel):
    sales_orders: List[SalesOrderResponse]
    total: int