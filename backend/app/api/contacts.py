from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse, ContactListResponse
from app.services.contacts import (
    create_contact as create_contact_service,
    get_contact as get_contact_service,
    get_contacts as get_contacts_service,
    update_contact as update_contact_service,
    delete_contact as delete_contact_service,
)

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse)
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    return create_contact_service(db, contact)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: UUID, db: Session = Depends(get_db)):
    return get_contact_service(db, contact_id)


@router.get("/", response_model=ContactListResponse)
async def get_contacts(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return get_contacts_service(db, limit, offset)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: UUID, contact: ContactUpdate, db: Session = Depends(get_db)):
    return update_contact_service(db, contact_id, contact)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: UUID, db: Session = Depends(get_db)):
    delete_contact_service(db, contact_id)
    return None