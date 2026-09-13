import time
import json
from pathlib import Path

class CacheManager:
    def __init__(self, cache_dir: str = "./.cache", ttl_seconds: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def get(self, key: str):
        file_path = self.cache_dir / f"{key}.json"
        if not file_path.exists():
            return None
        
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if time.time() - data["timestamp"] > self.ttl_seconds:
            file_path.unlink(missing_ok=True)
            return None
        return data["value"]

    def set(self, key: str, value):
        file_path = self.cache_dir / f"{key}.json"
        data = {
            "timestamp": time.time(),
            "value": value
        }
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")