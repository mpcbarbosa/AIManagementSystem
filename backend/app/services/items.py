import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from uuid import UUID

from app.models.item import Item
from app.schemas.items import (
    ItemCreate,
    ItemResponse,
    ItemListResponse,
    ItemUpdate,
)

logger = logging.getLogger(__name__)


def create_item(db: Session, item_data: ItemCreate) -> ItemResponse:
    # Check if code already exists
    if db.query(Item).filter(Item.code == item_data.code).first():
        raise HTTPException(status_code=409, detail=f"Item with code '{item_data.code}' already exists")

    item = Item(code=item_data.code, name=item_data.name, price=item_data.price)
    db.add(item)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict occurred")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error creating item", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    db.refresh(item)
    return ItemResponse(
        id=item.id,
        code=item.code,
        name=item.name,
        price=item.price,
        created_at=item.created_at,
        updated_at=item.updated_at
    )


def get_item(db: Session, item_id: UUID) -> ItemResponse:
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
    except Exception as e:
        logger.error("Error fetching item", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(
        id=item.id,
        code=item.code,
        name=item.name,
        price=item.price,
        created_at=item.created_at,
        updated_at=item.updated_at
    )


def get_items(db: Session, skip: int = 0, limit: int = 10) -> ItemListResponse:
    try:
        items = db.query(Item).offset(skip).limit(limit).all()
        total = db.query(Item).count()
    except Exception as e:
        logger.error("Error fetching items", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    return ItemListResponse(
        items=[
            ItemResponse(
                id=item.id,
                code=item.code,
                name=item.name,
                price=item.price,
                created_at=item.created_at,
                updated_at=item.updated_at
            ) for item in items
        ],
        total=total
    )


def update_item(db: Session, item_id: UUID, item_data: ItemUpdate) -> ItemResponse:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update fields if provided
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.price is not None:
        item.price = item_data.price

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict occurred")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error updating item", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    db.refresh(item)
    return ItemResponse(
        id=item.id,
        code=item.code,
        name=item.name,
        price=item.price,
        created_at=item.created_at,
        updated_at=item.updated_at
    )


def delete_item(db: Session, item_id: UUID):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.error("Integrity error deleting item", exc_info=True)
        raise HTTPException(status_code=500, detail="Error deleting item")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error deleting item", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")