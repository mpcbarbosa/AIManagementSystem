from sqlalchemy import String
from sqlalchemy.orm import relationship
from typing import List

from .base import Base

class Customer(Base):
    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    addresses: Mapped[List["Address"]] = relationship(back_populates="customer")