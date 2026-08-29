from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker
)

from app.config import Settings

settings = Settings()

DATABASE_PATH = Path("data/adacore.db")
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = settings.database_url

class Base(DeclarativeBase):
    pass

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def create_database() -> None:
    Base.metadata.create_all(engine)