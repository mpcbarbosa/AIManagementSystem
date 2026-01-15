from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Base

class Contact(Base):
    __tablename__ = "contacts"

    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    accepts_suggestions: Mapped[bool] = mapped_column(Boolean, nullable=True)