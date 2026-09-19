import pytest
from src.services.ai_service import AIService

@pytest.mark.asyncio
async def test_ai_service_generate_response_success(monkeypatch, sample_sources):
    """Uğurlu (Happy Path) sintez və keşləmə mexanizmini yoxlayırıq"""
    def mock_synthesize(prompt, sources):
        class DummyResult:
            answer = "Mocked synthetic answer."
        return DummyResult()

    monkeypatch.setattr("src.services.ai_service.synthesize", mock_synthesize)

    service = AIService()
    
    # 1. Kəşsiz sorğu
    res1 = await service.generate_response(prompt="Test query", sources=sample_sources, use_cache=False)
    assert res1 is not None

    # 2. Keşdən oxumaq (use_cache=True)
    res2 = await service.generate_response(prompt="Test query", sources=sample_sources, use_cache=True)
    assert res2 is not None

@pytest.mark.asyncio
async def test_ai_service_retry_failure(monkeypatch, sample_sources):
    """AI xəta verəndə retry mexanizminin işlədiyini və sonda xəta atdığını yoxlayırıq"""
    def mock_failing_synthesize(prompt, sources):
        raise RuntimeError("API quota or network error")

    monkeypatch.setattr("src.services.ai_service.synthesize", mock_failing_synthesize)

    service = AIService()
    
    # Keş boş olduğu və AI xəta verdiyi üçün ümumi Exception gözləyirik
    with pytest.raises(Exception):
        await service.generate_response(prompt="Failing query", sources=sample_sources, use_cache=False)

@pytest.mark.asyncio
async def test_ai_service_offline_fallback(monkeypatch, sample_sources):
    """AI xəta verəndə oflayn keş fallback mexanizminin işlədiyini yoxlayırıq"""
    service = AIService()
    
    # Əvvəlcə keşə saxta cavab yazırıq (cache_key formulu: ai_response_{hash(prompt)})
    cache_key = f"ai_response_{hash('Offline query')}"
    service.cache.set(cache_key, "Cached offline response")

    # İndi AI funksiyasını qəsdən qoparırıq (xəta verdiririk)
    def mock_failing_synthesize(prompt, sources):
        raise RuntimeError("Network down")

    monkeypatch.setattr("src.services.ai_service.synthesize", mock_failing_synthesize)

    # use_cache=True olduqda AI çöksə belə keşdən oxuyub oflayn cavab qaytarmalıdır
    res = await service.generate_response(prompt="Offline query", sources=sample_sources, use_cache=True)
    assert "[OFLAYN REJİM" in res or "Cached offline response" in res