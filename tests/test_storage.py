import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.storage.database import Base
from src.storage.repository import get_cached_response, save_response

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()

def test_save_and_get_cache(db_session):
    query = "AI nədir?"
    response = "AI süni intellektdir."
    
    save_response(db_session, query, response, "doc1.pdf")
    cached = get_cached_response(db_session, query)
    
    assert cached is not None
    assert cached.response_text == response
    assert cached.sources == "doc1.pdf"