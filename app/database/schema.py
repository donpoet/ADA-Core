from app.database.database import Base

from datetime import (
    datetime,
    UTC
)
from uuid import UUID

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.conversation.models import MessageRole

class ConversationModel(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    title: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    messages: Mapped[list["MessageModel"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False,
    )

    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    conversation: Mapped["ConversationModel"] = relationship(
        back_populates="messages"
    )