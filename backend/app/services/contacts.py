import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID
from typing import List

from app.models.customer import Customer
from app.models.contact import Contact
from app.schemas.contacts import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
)

logger = logging.getLogger(__name__)


def create_contact(db: Session, contact_data: ContactCreate) -> ContactResponse:
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == contact_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check phone uniqueness
    if db.query(Contact).filter(Contact.phone == contact_data.phone).first():
        raise HTTPException(status_code=409, detail=f"Contact phone {contact_data.phone} already exists")

    # Create contact
    contact = Contact(
        customer_id=contact_data.customer_id,
        phone=contact_data.phone,
        name=contact_data.name,
        accepts_suggestions=contact_data.accepts_suggestions
    )
    db.add(contact)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict occurred")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error creating contact", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    # Refresh
    db.refresh(contact)

    return ContactResponse(
        id=contact.id,
        customer_id=contact.customer_id,
        phone=contact.phone,
        name=contact.name,
        accepts_suggestions=contact.accepts_suggestions,
        created_at=contact.created_at,
        updated_at=contact.updated_at
    )


def get_contact(db: Session, contact_id: UUID) -> ContactResponse:
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
    except Exception as e:
        logger.error("Error fetching contact", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactResponse(
        id=contact.id,
        customer_id=contact.customer_id,
        phone=contact.phone,
        name=contact.name,
        accepts_suggestions=contact.accepts_suggestions,
        created_at=contact.created_at,
        updated_at=contact.updated_at
    )


def get_contacts(db: Session, limit: int = 10, offset: int = 0) -> ContactListResponse:
    try:
        contacts = db.query(Contact).limit(limit).offset(offset).all()
        total = db.query(Contact).count()
    except Exception as e:
        logger.error("Error fetching contacts", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    return ContactListResponse(
        contacts=[
            ContactResponse(
                id=c.id,
                customer_id=c.customer_id,
                phone=c.phone,
                name=c.name,
                accepts_suggestions=c.accepts_suggestions,
                created_at=c.created_at,
                updated_at=c.updated_at
            ) for c in contacts
        ],
        total=total
    )


def update_contact(db: Session, contact_id: UUID, contact_data: ContactUpdate) -> ContactResponse:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Update fields
    contact.name = contact_data.name
    contact.accepts_suggestions = contact_data.accepts_suggestions

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict occurred")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error updating contact", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    # Refresh
    db.refresh(contact)

    return ContactResponse(
        id=contact.id,
        customer_id=contact.customer_id,
        phone=contact.phone,
        name=contact.name,
        accepts_suggestions=contact.accepts_suggestions,
        created_at=contact.created_at,
        updated_at=contact.updated_at
    )


def delete_contact(db: Session, contact_id: UUID):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.error("Integrity error deleting contact", exc_info=True)
        raise HTTPException(status_code=500, detail="Error deleting contact")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error deleting contact", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")