import asyncio
import logging
from typing import Any

try:
    import httpx
except Exception:  # pragma: no cover - dependency guard
    httpx = None

from ai.schemas import Source
from ai.sources import fetch_arxiv, fetch_web, fetch_wikipedia
from src.config import settings
from src.services.ai_service import AIService

logger = logging.getLogger("orchestrator")


def _canonicalize_query(query: str) -> str:
    return (query or "").strip().lower()


def _normalize_sources(source_spec: str | None) -> list[str]:
    if not source_spec:
        return ["wikipedia", "arxiv", "web"]

    lookup = {
        "wiki": "wikipedia",
        "wikipedia": "wikipedia",
        "arxiv": "arxiv",
        "paper": "arxiv",
        "papers": "arxiv",
        "web": "web",
        "search": "web",
        "internet": "web",
    }

    ordered: list[str] = []
    seen: set[str] = set()
    for chunk in str(source_spec).split(","):
        name = lookup.get(chunk.strip().lower(), chunk.strip().lower())
        if name and name not in seen:
            ordered.append(name)
            seen.add(name)

    return ordered or ["wikipedia", "arxiv", "web"]


async def _fetch_one_source(
    source_name: str,
    query: str,
    *,
    max_results: int = 2,
) -> list[Source]:
    # Hər mənbənin özünəməxsus başlıqlarını təyin edirik ki, 406 xətası alınmasın
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ResearchAssistant/1.0"
    }
    if source_name == "arxiv":
        headers["Accept"] = "application/atom+xml,application/xml"
    elif source_name == "wikipedia":
        headers["Accept"] = "application/json"
    else:
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

    async with httpx.AsyncClient(
        timeout=settings.per_source_timeout_seconds + 5,
        follow_redirects=True,
        headers=headers,
    ) as client:
        async with asyncio.timeout(settings.per_source_timeout_seconds):
            if source_name == "wikipedia":
                return await fetch_wikipedia(query, max_results=max_results, client=client)
            if source_name == "arxiv":
                return await fetch_arxiv(query, max_results=max_results, client=client)
            if source_name == "web":
                return await fetch_web(query, max_results=max_results, client=client)
            return []


async def gather_sources(
    query: str,
    ai_service: AIService | None = None,
    sources_to_use: str = "",
    *,
    max_results: int = 2,
) -> list[Source]:
    """Fetch sources from Wikipedia, arXiv, and web search concurrently."""
    canonical_query = _canonicalize_query(query)
    allowed_sources = _normalize_sources(sources_to_use)
    logger.info("Fetching sources for query=%r via %s", canonical_query, allowed_sources)

    tasks = [
        asyncio.create_task(
            _fetch_one_source(name, canonical_query, max_results=max_results)
        )
        for name in allowed_sources
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    combined: list[Source] = []
    for item in results:
        if isinstance(item, Exception):
            logger.warning("One source failed and was skipped: %s", item)
            continue
        if item:
            combined.extend(item)

    logger.info("Total sources gathered: %d", len(combined))
    return combined


async def fetch_sources_sequential(
    query: str,
    sources_to_use: str = "",
    *,
    max_results: int = 2,
) -> list[Source]:
    """Sequential source acquisition for benchmarking and fallback comparisons."""
    canonical_query = _canonicalize_query(query)
    combined: list[Source] = []
    for source_name in _normalize_sources(sources_to_use):
        try:
            fetched = await _fetch_one_source(source_name, canonical_query, max_results=max_results)
            combined.extend(fetched)
        except Exception as exc:  # pragma: no cover - network edge case
            logger.warning("Sequential fetch for %s failed: %s", source_name, exc)
    return combined


async def answer_question(query: str, sources_str: str = "", use_cache: bool = True) -> str:
    """Run the full source-fetch + synthesis pipeline."""
    canonical_query = _canonicalize_query(query)
    ai_service = AIService()
    sources = await gather_sources(canonical_query, ai_service, sources_str)

    if not sources:
        return "No sources were found for this question."

    answer = await ai_service.generate_response(canonical_query, sources, use_cache=use_cache)
    return answer