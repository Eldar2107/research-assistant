from sqlalchemy.orm import Session
from src.storage.models import QueryCache

def get_cached_response(db: Session, query: str):
    return db.query(QueryCache).filter(QueryCache.query_text == query).first()

def save_response(db: Session, query: str, response: str, sources: str = ""):
    existing = get_cached_response(db, query)
    if existing:
        existing.response_text = response
        existing.sources = sources
        db.commit()
        db.refresh(existing)
        return existing

    cache_entry = QueryCache(query_text=query, response_text=response, sources=sources)
    db.add(cache_entry)
    db.commit()
    db.refresh(cache_entry)
    return cache_entry