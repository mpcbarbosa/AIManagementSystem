import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import insert
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, timezone
from typing import List

from app.models.sales_order import SalesOrder, sales_order_items
from app.models.customer import Customer
from app.models.contact import Contact
from app.models.address import Address
from app.models.item import Item
from app.schemas.sales_orders import (
    SalesOrderCreate,
    SalesOrderResponse,
    SalesOrderListResponse,
    SalesOrderItemResponse,
)

logger = logging.getLogger(__name__)


def create_sales_order(db: Session, order_data: SalesOrderCreate) -> SalesOrderResponse:
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Validate contact exists and belongs to customer
    contact = db.query(Contact).filter(Contact.id == order_data.contact_id, Contact.customer_id == order_data.customer_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found or does not belong to customer")

    # Validate address exists and belongs to customer
    address = db.query(Address).filter(Address.id == order_data.address_id, Address.customer_id == order_data.customer_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found or does not belong to customer")

    # Validate all items exist
    item_ids = [item.item_id for item in order_data.items]
    items = db.query(Item).filter(Item.id.in_(item_ids)).all()
    if len(items) != len(item_ids):
        raise HTTPException(status_code=404, detail="One or more items not found")

    item_dict = {item.id: item for item in items}

    # Create sales order
    order = SalesOrder(
        customer_id=order_data.customer_id,
        contact_id=order_data.contact_id,
        address_id=order_data.address_id,
        order_date=datetime.now(timezone.utc),
        status="draft"
    )
    db.add(order)
    db.flush()  # to get id

    # Insert items into association table
    order_items = []
    order_total = 0.0
    for order_item in order_data.items:
        item = item_dict[order_item.item_id]
        unit_price = item.price
        line_total = order_item.quantity * unit_price
        order_total += line_total
        order_items.append({
            'sales_order_id': order.id,
            'item_id': order_item.item_id,
            'quantity': order_item.quantity,
            'unit_price': unit_price
        })

    db.execute(insert(sales_order_items), order_items)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict occurred")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error creating sales order", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    # Build response
    return _build_sales_order_response(order, items, order_items)


def get_sales_order(db: Session, order_id: UUID) -> SalesOrderResponse:
    try:
        order = db.query(SalesOrder).options(
            joinedload(SalesOrder.customer),
            joinedload(SalesOrder.contact),
            joinedload(SalesOrder.address),
            joinedload(SalesOrder.items)
        ).filter(SalesOrder.id == order_id).first()
    except Exception as e:
        logger.error("Error fetching sales order", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")

    # Get items with quantities and prices
    items_data = db.execute(
        sales_order_items.select().where(sales_order_items.c.sales_order_id == order_id)
    ).fetchall()

    items = db.query(Item).filter(Item.id.in_([row.item_id for row in items_data])).all()
    item_dict = {item.id: item for item in items}

    order_items = []
    order_total = 0.0
    for row in items_data:
        item = item_dict[row.item_id]
        line_total = row.quantity * row.unit_price
        order_total += line_total
        order_items.append({
            'sales_order_id': order.id,
            'item_id': row.item_id,
            'quantity': row.quantity,
            'unit_price': row.unit_price,
            'line_total': line_total,
            'item': item
        })

    return _build_sales_order_response(order, items, order_items)


def get_sales_orders(db: Session, limit: int = 10, offset: int = 0) -> SalesOrderListResponse:
    try:
        orders = db.query(SalesOrder).options(
            joinedload(SalesOrder.customer),
            joinedload(SalesOrder.contact),
            joinedload(SalesOrder.address),
            joinedload(SalesOrder.items)
        ).limit(limit).offset(offset).all()
        total = db.query(SalesOrder).count()
    except Exception as e:
        logger.error("Error fetching sales orders", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    sales_orders = []
    for order in orders:
        # Similar to get_sales_order
        items_data = db.execute(
            sales_order_items.select().where(sales_order_items.c.sales_order_id == order.id)
        ).fetchall()

        items = db.query(Item).filter(Item.id.in_([row.item_id for row in items_data])).all()
        item_dict = {item.id: item for item in items}

        order_items = []
        order_total = 0.0
        for row in items_data:
            item = item_dict[row.item_id]
            line_total = row.quantity * row.unit_price
            order_total += line_total
            order_items.append({
                'sales_order_id': order.id,
                'item_id': row.item_id,
                'quantity': row.quantity,
                'unit_price': row.unit_price,
                'line_total': line_total,
                'item': item
            })

        sales_orders.append(_build_sales_order_response(order, items, order_items))

    return SalesOrderListResponse(sales_orders=sales_orders, total=total)


def update_sales_order(db: Session, order_id: UUID, order_data: SalesOrderCreate) -> SalesOrderResponse:
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")

    # Validate customer, contact, address same as create
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    contact = db.query(Contact).filter(Contact.id == order_data.contact_id, Contact.customer_id == order_data.customer_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found or does not belong to customer")

    address = db.query(Address).filter(Address.id == order_data.address_id, Address.customer_id == order_data.customer_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found or does not belong to customer")

    item_ids = [item.item_id for item in order_data.items]
    items = db.query(Item).filter(Item.id.in_(item_ids)).all()
    if len(items) != len(item_ids):
        raise HTTPException(status_code=404, detail="One or more items not found")

    item_dict = {item.id: item for item in items}

    # Update order
    order.customer_id = order_data.customer_id
    order.contact_id = order_data.contact_id
    order.address_id = order_data.address_id

    # Delete existing items
    db.execute(sales_order_items.delete().where(sales_order_items.c.sales_order_id == order_id))

    # Insert new items
    order_items = []
    order_total = 0.0
    for order_item in order_data.items:
        item = item_dict[order_item.item_id]
        unit_price = item.price
        line_total = order_item.quantity * unit_price
        order_total += line_total
        order_items.append({
            'sales_order_id': order.id,
            'item_id': order_item.item_id,
            'quantity': order_item.quantity,
            'unit_price': unit_price
        })

    db.execute(insert(sales_order_items), order_items)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict occurred")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error updating sales order", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

    # Reload and build response
    order = db.query(SalesOrder).options(
        joinedload(SalesOrder.customer),
        joinedload(SalesOrder.contact),
        joinedload(SalesOrder.address),
        joinedload(SalesOrder.items)
    ).filter(SalesOrder.id == order_id).first()

    return _build_sales_order_response(order, items, order_items)


def delete_sales_order(db: Session, order_id: UUID):
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")

    # Delete items
    db.execute(sales_order_items.delete().where(sales_order_items.c.sales_order_id == order_id))

    # Delete order
    db.delete(order)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.error("Integrity error deleting sales order", exc_info=True)
        raise HTTPException(status_code=500, detail="Error deleting sales order")
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error deleting sales order", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


def _build_sales_order_response(order: SalesOrder, items: List[Item], order_items: List[dict]) -> SalesOrderResponse:
    item_dict = {item.id: item for item in items}
    items_response = []
    order_total = 0.0
    for oi in order_items:
        item = item_dict[oi['item_id']]
        line_total = oi['quantity'] * oi['unit_price']
        order_total += line_total
        items_response.append(SalesOrderItemResponse(
            item_id=item.id,
            name=item.name,
            price=item.price,
            quantity=oi['quantity'],
            unit_price=oi['unit_price'],
            line_total=line_total
        ))

    return SalesOrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        contact_id=order.contact_id,
        address_id=order.address_id,
        order_date=order.order_date,
        status=order.status,
        items=items_response,
        order_total=order_total,
        created_at=order.created_at,
        updated_at=order.updated_at
    )