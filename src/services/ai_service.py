import logging
import asyncio
from typing import Callable, Any
from src.config import settings
from src.services.cache import CacheManager
from ai import synthesize

# Loqlaşdırma tənzimləməsi
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ai_service")

class AIService:
    def __init__(self):
        # JSON əsaslı File Cache-i işə salırıq
        self.cache = CacheManager(
            cache_dir=settings.cache_dir,
            ttl_seconds=settings.cache_ttl_seconds
        )

    async def execute_resilient(
        self, 
        func: Callable, 
        *args, 
        retries: int = 3, 
        timeout_seconds: int = settings.per_source_timeout_seconds, 
        **kwargs
    ) -> Any:
        """
        ai/ modulundakı API çağırışlarını Timeout və Retry ilə qoruyan funksiya.
        """
        func_name = func.__name__
        
        for attempt in range(1, retries + 1):
            try:
                logger.debug(f"[{func_name}] İcra edilir... (Cəhd {attempt}/{retries})")
                
                # Funksiya async-dirsə
                if asyncio.iscoroutinefunction(func):
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
                # Funksiya sinxrondursa (məs. synthesize)
                else:
                    return await asyncio.wait_for(
                        asyncio.to_thread(func, *args, **kwargs), 
                        timeout=timeout_seconds
                    )

            except asyncio.TimeoutError:
                logger.warning(f"🕒 [{func_name}] Gözləmə vaxtı bitdi ({timeout_seconds}s). (Cəhd {attempt}/{retries})")
            except Exception as e:
                logger.error(f"❌ [{func_name}] Xəta baş verdi: {e}. (Cəhd {attempt}/{retries})")
            
            if attempt == retries:
                logger.error(f"🚨 [{func_name}] Bütün {retries} cəhd uğursuz oldu!")
                raise Exception(f"{func_name} əməliyyatı tamamilə uğursuz oldu.")
            
            # Exponential backoff (2, 4 saniyə gözləmə)
            sleep_time = 2 ** attempt
            logger.info(f"🔄 {sleep_time} saniyə sonra yenidən cəhd edilir...")
            await asyncio.sleep(sleep_time)

    async def generate_response(self, prompt: str, sources: list, use_cache: bool = True):
        """
        Keşi yoxlayır, yoxdursa təhlükəsiz şəkildə ai.synthesize çağırır və nəticəni keşləyir.
        """
        cache_key = f"ai_response_{hash(prompt)}"
        
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info("⚡ Nəticə aktiv keşdən (JSON) uğurla gətirildi.")
                return cached_result

        # Birbaşa Gemini əvəzinə layihənin tələb etdiyi ai.synthesize funksiyasını çağırırıq
        logger.info("🤖 Süni intellekt məlumatları sintez edir...")
        answer = await self.execute_resilient(synthesize, prompt, sources, timeout_seconds=30)
        
        # Nəticəni JSON keşinə yazırıq
        if use_cache:
            self.cache.set(cache_key, answer)

        return answer