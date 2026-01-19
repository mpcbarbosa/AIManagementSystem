from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import List


class ItemCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., ge=0)

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty or whitespace')
        return v.strip()

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()


class ItemUpdate(BaseModel):
    name: str = Field(None, min_length=1, max_length=255)
    price: float = Field(None, ge=0)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip() if v else v


class ItemResponse(BaseModel):
    id: UUID
    code: str
    name: str
    price: float
    created_at: datetime
    updated_at: datetime


class ItemListResponse(BaseModel):
    items: List[ItemResponse]
    total: int