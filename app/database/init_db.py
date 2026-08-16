from sqlalchemy import create_engine

from app.config import Settings
from app.database.database import Base
from app.database.schema import ConversationModel, MessageModel

def main() -> None:
    settings = Settings()
    engine = create_engine(settings.database_url)

    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()