from src.config import settings
from src.services.cache import CacheManager

class AIService:
    def __init__(self):
        self.cache = CacheManager(
            cache_dir=settings.cache_dir,
            ttl_seconds=settings.cache_ttl_seconds
        )

    async def generate_response(self, prompt: str, use_cache: bool = True) -> str:
        cache_key = f"ai_response_{settings.llm_provider}_{hash(prompt)}"
        
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result

        # Burada seçilmiş provider-ə uyğun LLM çağırışı həyata keçirilir
        # Hazırda təməl strukturu qururuq, gələcəkdə API inteqrasiyası genişləndiriləcək
        response_text = f"[{settings.llm_provider.upper()} - {settings.llm_model}] Cavab: {prompt} (Simulyasiya edilmiş nəticə)"

        if use_cache:
            self.cache.set(cache_key, response_text)

        return response_text