from typing import AsyncIterator
import httpx
from openai import AsyncOpenAI
from app.providers.base import BaseLLMProvider
from app.schemas import ChatRequest


class OpenRouterProvider(BaseLLMProvider):
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str, model: str = "qwen/qwen3-235b-a22b:free"):
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.BASE_URL,
            http_client=httpx.AsyncClient(trust_env=False),
        )
        self.model = model

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        messages = [{"role": message.role, "content": message.content} for message in request.messages]
        stream = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )
        async for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield token

    async def health_check(self) -> bool:
        try:
            models = await self._client.models.list()
            return len(models.data) > 0
        except Exception:
            return False
