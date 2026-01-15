from sqlalchemy import String, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from sqlalchemy.orm import relationship

from .base import Base

class Address(Base):
    __tablename__ = "addresses"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    alias_normalized: Mapped[str] = mapped_column(String(255), computed("lower(trim(alias))"), stored=True)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="addresses")

    __table_args__ = (UniqueConstraint('customer_id', 'alias_normalized'),)