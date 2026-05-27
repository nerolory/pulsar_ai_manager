from typing import AsyncIterator
import httpx
from openai import AsyncOpenAI
from app.providers.base import BaseLLMProvider
from app.schemas import ChatRequest
from loguru import logger


class VseLLMProvider(BaseLLMProvider):
    BASE_URL = "https://api.vsellm.ru/v1"

    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini"):
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.BASE_URL,
            http_client=httpx.AsyncClient(trust_env=False),
        )
        self.model = model

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        messages = [
            {"role": message.role, "content": message.content if isinstance(message.content, str) else [part.model_dump(exclude_none=True) for part in message.content]}
            for message in request.messages
        ]
        for message in messages:
            if isinstance(message["content"], list):
                logger.info(f"[VseLLM] multimodal msg parts: {[part['type'] for part in message['content']]}")
            else:
                logger.info(f"[VseLLM] text msg len={len(message['content'])}")
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
