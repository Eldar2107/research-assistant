import os
from google import genai
from src.config import settings
from src.services.cache import CacheManager

class AIService:
    def __init__(self):
        self.cache = CacheManager(
            cache_dir=settings.cache_dir,
            ttl_seconds=settings.cache_ttl_seconds
        )
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY tapılmadı!")
        self.client = genai.Client(api_key=api_key)

    async def generate_response(self, prompt: str, use_cache: bool = True) -> str:
        cache_key = f"ai_response_{settings.llm_provider}_{hash(prompt)}"
        
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                print("-> (Keşdən oxundu)")
                return cached_result

        response = self.client.models.generate_content(
            model=settings.llm_model,
            contents=prompt,
        )
        response_text = response.text

        if use_cache:
            self.cache.set(cache_key, response_text)

        return response_text