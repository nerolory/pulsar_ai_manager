import asyncio
from typing import AsyncIterator
from app.providers.base import BaseLLMProvider
from app.schemas import ChatRequest


MOCK_RESPONSE = (
    "Это тестовый ответ от **MockProvider**. "
    "Бекенд работает корректно. "
    "Подключите реального провайдера в настройках."
)


class MockProvider(BaseLLMProvider):
    model = "mock"

    async def chat(self, request: ChatRequest) -> AsyncIterator[str]:
        for word in MOCK_RESPONSE.split():
            yield word + " "
            await asyncio.sleep(0.05)

    async def health_check(self) -> bool:
        return True
