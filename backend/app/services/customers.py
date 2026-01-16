from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID
from typing import List

from app.models.customer import Customer
from app.models.address import Address
from app.models.contact import Contact
from app.schemas.customers import (
    CustomerCreate,
    CustomerResponse,
    CustomerListResponse,
    AddressResponse,
)


def create_customer(db: Session, customer_data: CustomerCreate) -> CustomerResponse:
    # Check contacts uniqueness
    for contact in customer_data.contacts:
        if db.query(Contact).filter(Contact.phone == contact.phone).first():
            raise HTTPException(status_code=409, detail=f"Contact phone {contact.phone} already exists")

    # Create customer
    customer = Customer(name=customer_data.name)
    db.add(customer)
    db.flush()  # to get id

    # Create addresses
    addresses = []
    for addr in customer_data.addresses:
        alias_norm = addr.alias.lower().strip()
        # Check if alias_norm exists for this customer
        if db.query(Address).filter(Address.customer_id == customer.id, Address.alias_normalized == alias_norm).first():
            raise HTTPException(status_code=409, detail=f"Address alias '{addr.alias}' already exists for this customer")
        address = Address(customer_id=customer.id, alias=addr.alias, street=addr.street, city=addr.city)
        db.add(address)
        addresses.append(address)

    # Create contacts
    contacts = []
    for cont in customer_data.contacts:
        contact = Contact(customer_id=customer.id, phone=cont.phone, name=cont.name, accepts_suggestions=cont.accepts_suggestions)
        db.add(contact)
        contacts.append(contact)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict occurred")

    # Refresh
    db.refresh(customer)
    for addr in addresses:
        db.refresh(addr)
    for cont in contacts:
        db.refresh(cont)

    # Build response
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        addresses=[
            AddressResponse(
                id=a.id,
                alias=a.alias,
                street=a.street,
                city=a.city,
                created_at=a.created_at,
                updated_at=a.updated_at
            ) for a in addresses
        ],
        contacts=[
            ContactResponse(
                id=c.id,
                phone=c.phone,
                name=c.name,
                accepts_suggestions=c.accepts_suggestions,
                created_at=c.created_at,
                updated_at=c.updated_at
            ) for c in contacts
        ],
        created_at=customer.created_at,
        updated_at=customer.updated_at
    )


def get_customer(db: Session, customer_id: UUID) -> CustomerResponse:
    customer = db.query(Customer).options(joinedload(Customer.addresses), joinedload(Customer.contacts)).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        addresses=[
            AddressResponse(
                id=a.id,
                alias=a.alias,
                street=a.street,
                city=a.city,
                created_at=a.created_at,
                updated_at=a.updated_at
            ) for a in customer.addresses
        ],
        contacts=[
            ContactResponse(
                id=c.id,
                phone=c.phone,
                name=c.name,
                accepts_suggestions=c.accepts_suggestions,
                created_at=c.created_at,
                updated_at=c.updated_at
            ) for c in customer.contacts
        ],
        created_at=customer.created_at,
        updated_at=customer.updated_at
    )


def get_customers(db: Session, limit: int = 10, offset: int = 0) -> CustomerListResponse:
    customers = db.query(Customer).options(joinedload(Customer.addresses), joinedload(Customer.contacts)).limit(limit).offset(offset).all()
    total = db.query(Customer).count()
    return CustomerListResponse(
        customers=[
            CustomerResponse(
                id=c.id,
                name=c.name,
                addresses=[
                    AddressResponse(
                        id=a.id,
                        alias=a.alias,
                        street=a.street,
                        city=a.city,
                        created_at=a.created_at,
                        updated_at=a.updated_at
                    ) for a in c.addresses
                ],
                contacts=[
                    ContactResponse(
                        id=ct.id,
                        phone=ct.phone,
                        name=ct.name,
                        accepts_suggestions=ct.accepts_suggestions,
                        created_at=ct.created_at,
                        updated_at=ct.updated_at
                    ) for ct in c.contacts
                ],
                created_at=c.created_at,
                updated_at=c.updated_at
            ) for c in customers
        ],
        total=total
    )


def update_customer(db: Session, customer_id: UUID, customer_data: CustomerCreate) -> CustomerResponse:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Update name
    customer.name = customer_data.name

    # Check for duplicate aliases in the request payload
    alias_norms = set()
    for addr in customer_data.addresses:
        alias_norm = addr.alias.lower().strip()
        if alias_norm in alias_norms:
            raise HTTPException(status_code=409, detail=f"Address alias '{addr.alias}' appears multiple times in the request")
        alias_norms.add(alias_norm)

    # Replace addresses
    db.query(Address).filter(Address.customer_id == customer_id).delete()

    addresses = []
    for addr in customer_data.addresses:
        address = Address(customer_id=customer_id, alias=addr.alias, street=addr.street, city=addr.city)
        db.add(address)
        addresses.append(address)

    # Ignore contacts for update

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict occurred")

    # Reload customer with addresses and contacts
    customer = db.query(Customer).options(joinedload(Customer.addresses), joinedload(Customer.contacts)).filter(Customer.id == customer_id).first()

    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        addresses=[
            AddressResponse(
                id=a.id,
                alias=a.alias,
                street=a.street,
                city=a.city,
                created_at=a.created_at,
                updated_at=a.updated_at
            ) for a in customer.addresses
        ],
        contacts=[
            ContactResponse(
                id=c.id,
                phone=c.phone,
                name=c.name,
                accepts_suggestions=c.accepts_suggestions,
                created_at=c.created_at,
                updated_at=c.updated_at
            ) for c in customer.contacts
        ],
        created_at=customer.created_at,
        updated_at=customer.updated_at
    )


def delete_customer(db: Session, customer_id: UUID):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Delete addresses
    db.query(Address).filter(Address.customer_id == customer_id).delete()

    # Delete customer
    db.delete(customer)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting customer")