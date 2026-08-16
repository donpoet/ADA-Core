import pytest
from sqlalchemy import create_engine
from pathlib import Path

from app.database.database import Base

@pytest.fixture
def db_engine():
    test_directory = Path(".pytest-temp").resolve()
    test_directory.mkdir(exist_ok=True)
    
    database_path = test_directory / "test.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()

    if database_path.exists():
        database_path.unlink()