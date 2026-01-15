from datetime import datetime
from sqlalchemy import String, UUID, ForeignKey
from sqlalchemy.orm import relationship, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime



import uuid

from .base import Base

class Chat(Base):
    __tablename__ = "chats"

    contact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # 'in' or 'out'
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    contact: Mapped["Contact"] = relationship()