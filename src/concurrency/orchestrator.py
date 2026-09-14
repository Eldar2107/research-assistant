import asyncio
import httpx
from typing import List
import logging
from ai.sources import fetch_wikipedia, fetch_arxiv, fetch_web
from src.services.ai_service import AIService

logger = logging.getLogger("orchestrator")

async def gather_sources(query: str, ai_service: AIService, sources_to_use: str = "") -> List:
    """
    Mənbələrdən (Wiki, Arxiv, Web) məlumatları eyni anda (paralel) çəkir.
    """
    logger.info(f"🔍 '{query}' üçün mənbələr axtarılır...")
    
    # Hansı mənbələrin istifadə ediləcəyini müəyyən edirik
    allowed_sources = [s.strip().lower() for s in sources_to_use.split(",")] if sources_to_use else ["wiki", "arxiv", "web"]
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        tasks = []
        
        if "wiki" in allowed_sources:
            tasks.append(ai_service.execute_resilient(fetch_wikipedia, query, max_results=2, client=client))
        if "arxiv" in allowed_sources:
            tasks.append(ai_service.execute_resilient(fetch_arxiv, query, max_results=2, client=client))
        if "web" in allowed_sources:
            tasks.append(ai_service.execute_resilient(fetch_web, query, max_results=2, client=client))

        # asyncio.gather ilə bütün axtarışları paralel (eyni anda) işə salırıq
        # return_exceptions=True -> biri çöksə, digərləri işləməyə davam etsin
        results = await asyncio.gather(*tasks, return_exceptions=True)

    combined_sources = []
    for r in results:
        if isinstance(r, Exception):
            logger.warning(f"⚠️ Mənbələrdən birində xəta oldu və atlandı: {r}")
            continue
        if r:
            combined_sources.extend(r)
            
    logger.info(f"✅ Ümumilikdə {len(combined_sources)} mənbə tapıldı.")
    return combined_sources

async def answer_question(query: str, sources_str: str = "", use_cache: bool = True) -> str:
    """
    Bütün prosesi idarə edir: Axtarış + AI Sintezi
    """
    ai_service = AIService()
    
    # 1. Mənbələri tap
    sources = await gather_sources(query, ai_service, sources_str)
    
    if not sources:
        return "Təəssüf ki, heç bir mənbə tapılmadı və cavab hazırlana bilmədi."
    
    # 2. AI-a göndər (sizin yazdığınız təhlükəsiz metod vasitəsilə)
    answer = await ai_service.generate_response(query, sources, use_cache=use_cache)
    
    return answer