import asyncio
from typing import AsyncIterator, List
from app.providers.base import BaseLLMProvider
from app.schemas import ChatRequest, ProviderCapabilities, ModelInfo


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

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_caching=False,
            supports_images=False,
            supports_pdf=False,
            supports_system_prompt=True,
            supports_files=[],
            max_context_tokens=4096,
            streaming=True,
            pricing_model="per_request",
            has_balance_api=False,
            has_models_list=False,
            free_tier_available=True,
        )

    async def list_models(self) -> List[ModelInfo]:
        return [ModelInfo(
            id="mock",
            name="Mock Model",
            context_length=4096,
            pricing=None,
            free_tier=True,
        )]
