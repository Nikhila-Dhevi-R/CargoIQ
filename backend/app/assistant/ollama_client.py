from typing import Optional, Dict, Any, List
import httpx
from app.core.config import settings
from app.core.logging import logger

class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Queries local Ollama instance with streaming/full response."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("message", {}).get("content", "").strip()
                else:
                    logger.warning(f"Ollama returned HTTP status {resp.status_code}: {resp.text}")
                    return None
        except Exception as e:
            logger.warning(f"Ollama query failed: {e}. Utilizing grounded algorithmic response synthesis.")
            return None

ollama_client = OllamaClient()
