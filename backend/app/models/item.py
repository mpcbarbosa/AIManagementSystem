from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base

class Item(Base):
    __tablename__ = "items"

    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)