from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class AddressCreate(BaseModel):
    alias: str
    street: str
    city: str


class AddressResponse(BaseModel):
    id: UUID
    alias: str
    street: str
    city: str
    created_at: datetime
    updated_at: datetime


class ContactCreate(BaseModel):
    phone: str
    name: str
    accepts_suggestions: Optional[bool] = None


class ContactResponse(BaseModel):
    id: UUID
    phone: str
    name: str
    accepts_suggestions: Optional[bool]
    created_at: datetime
    updated_at: datetime


class CustomerCreate(BaseModel):
    name: str
    addresses: List[AddressCreate] = Field(default_factory=list)
    contacts: List[ContactCreate] = Field(default_factory=list)


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    addresses: List[AddressResponse]
    contacts: List[ContactResponse]
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int