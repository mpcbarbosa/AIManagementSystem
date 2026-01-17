from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class ContactCreate(BaseModel):
    customer_id: UUID
    phone: str
    name: str
    accepts_suggestions: Optional[bool] = None


class ContactUpdate(BaseModel):
    name: str
    accepts_suggestions: Optional[bool] = None


class ContactResponse(BaseModel):
    id: UUID
    customer_id: UUID
    phone: str
    name: str
    accepts_suggestions: Optional[bool]
    created_at: datetime
    updated_at: datetime


class ContactListResponse(BaseModel):
    contacts: List[ContactResponse]
    total: int