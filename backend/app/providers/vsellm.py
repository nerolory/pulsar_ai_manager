from typing import AsyncIterator
from openai import AsyncOpenAI
from app.providers.base import BaseLLMProvider
from app.schemas import ChatRequest


class VseLLMProvider(BaseLLMProvider):
    BASE_URL = "https://api.vsellm.ru/v1"

    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini"):
        self._client = AsyncOpenAI(api_key=api_key, base_url=self.BASE_URL)
        self.model = model

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        stream = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def health_check(self) -> bool:
        try:
            models = await self._client.models.list()
            return len(models.data) > 0
        except Exception:
            return False
