from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas.items import ItemCreate, ItemResponse, ItemListResponse, ItemUpdate
from app.services.items import (
    create_item as create_item_service,
    get_item as get_item_service,
    get_items as get_items_service,
    update_item as update_item_service,
    delete_item as delete_item_service,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return create_item_service(db, item)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: UUID, db: Session = Depends(get_db)):
    return get_item_service(db, item_id)


@router.get("/", response_model=ItemListResponse)
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return get_items_service(db, skip, limit)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: UUID, item: ItemUpdate, db: Session = Depends(get_db)):
    return update_item_service(db, item_id, item)


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: UUID, db: Session = Depends(get_db)):
    delete_item_service(db, item_id)
    return None