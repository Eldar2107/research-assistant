from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from src.storage.database import Base


class QueryCache(Base):
    __tablename__ = "query_cache"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String, unique=True, index=True, nullable=False)
    response_text = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))