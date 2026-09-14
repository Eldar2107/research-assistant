from sqlalchemy.orm import Session
from src.storage.models import QueryCache

def get_cached_response(db: Session, query: str):
    return db.query(QueryCache).filter(QueryCache.query_text == query).first()

def save_response(db: Session, query: str, response: str, sources: str = ""):
    cache_entry = QueryCache(query_text=query, response_text=response, sources=sources)
    db.add(cache_entry)
    db.commit()
    db.refresh(cache_entry)
    return cache_entry