from uuid import (
    uuid4,
    UUID
)
from sqlalchemy.orm import Session

from app.conversation.store import ConversationStore
from app.conversation.models import (
    Conversation,
    Message
)
from app.database.schema import (
    ConversationModel,
    MessageModel
)
from datetime import (
    datetime,
    UTC
)

class SQLiteConversationStore(ConversationStore):

    def __init__(self, engine):
        self._engine = engine

    def create(self) -> Conversation:
        conversation = Conversation(
            messages=[],
            )
        
        db_conversation = ConversationModel(
            id=str(conversation.id)
        )

        with Session(self._engine) as session:
            session.add(db_conversation)
            session.commit()

        return conversation

    def get(self, conversation_id:UUID) -> Conversation:
        with Session(self._engine) as session:
            result = session.get(
                ConversationModel,
                str(conversation_id),
            )

            if result is None:
                raise ValueError(
                    f"Conversation {conversation_id} not found"
                )
            
            messages = [
                Message(
                    id=UUID(message.id),
                    role=message.role,
                    content=message.content,
                )
                for message in result.messages
            ]

            return Conversation(
                id=UUID(result.id),
                title=result.title,
                created_at=ensure_utc(result.created_at),
                updated_at=ensure_utc(result.updated_at),
                messages=messages,
            )

    def save(self, conversation:Conversation) -> None:
        with Session(self._engine) as session:
            conversation_model = session.get(
                ConversationModel,
                str(conversation.id),
            )

            if conversation_model is None:
                conversation_model = ConversationModel(
                    id=str(conversation.id),
                    title=conversation.title,
                    created_at=ensure_utc(conversation.created_at),
                    updated_at=ensure_utc(conversation.updated_at)
                )
                session.add(conversation_model)

            conversation_model.messages = [
                MessageModel(
                    id=str(message.id),
                    role=message.role,
                    content=message.content,
                )
                for message in conversation.messages
            ]

            session.commit()

    def list_conversations(self) -> list[Conversation]:
        conversations = []
        with Session(self._engine) as session:
            conversation_models = session.query(ConversationModel).all()
        
            for conversation_model in conversation_models:
                messages = [
                    Message(
                        id=UUID(message.id),
                        role=message.role,
                        content=message.content
                    )
                    for message in conversation_model.messages 
                ]
                conversations.append(
                    Conversation(
                        id=UUID(conversation_model.id),
                        title=conversation_model.title,
                        created_at=ensure_utc(conversation_model.created_at),
                        updated_at=ensure_utc(conversation_model.updated_at),
                        messages=messages
                    )
                )
        return conversations


def ensure_utc(value: datetime) -> datetime:
    if(value.tzinfo is None):
        return value.replace(tzinfo=UTC)
    
    return value.astimezone(UTC)