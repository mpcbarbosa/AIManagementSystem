from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Base

class Item(Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)