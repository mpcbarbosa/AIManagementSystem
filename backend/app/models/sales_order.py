from datetime import datetime
from sqlalchemy import String, UUID, ForeignKey, Table, Column, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Base

# Association table for sales order items
sales_order_items = Table(
    'sales_order_items',
    Base.metadata,
    Column('sales_order_id', UUID(as_uuid=True), ForeignKey('sales_orders.id'), primary_key=True),
    Column('item_id', UUID(as_uuid=True), ForeignKey('items.id'), primary_key=True),
    Column('quantity', Integer, nullable=False),
    Column('unit_price', Float, nullable=False),
)

class SalesOrder(Base):
    __tablename__ = "sales_orders"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    contact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)
    address_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    customer: Mapped["Customer"] = relationship()
    contact: Mapped["Contact"] = relationship()
    address: Mapped["Address"] = relationship()
    items: Mapped[List["Item"]] = relationship(secondary=sales_order_items)