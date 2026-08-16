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

class SQLiteConversationStore(ConversationStore):

    def __init__(self, engine):
        self._engine = engine

    def create(self) -> Conversation:
        conversation = Conversation(
            id=uuid4(),
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