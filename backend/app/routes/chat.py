"""Chat streaming route for LLM completions.

Handles streaming chat requests to the active LLM provider, including
system prompt injection and context window management.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest
from app.state import get_provider
from app.exceptions import (
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    BalanceError,
    NetworkError,
    ProviderUnavailableError,
    InvalidRequestError,
)
from loguru import logger

router = APIRouter(prefix="/chat", tags=["chat"])


def _provider_error_to_http(exc: ProviderError) -> HTTPException:
    """Map typed provider errors to HTTP responses for pre-stream failures."""
    if isinstance(exc, AuthenticationError):
        return HTTPException(
            status_code=401,
            detail={"error": "Ошибка аутентификации", "message": exc.message},
        )
    if isinstance(exc, RateLimitError):
        return HTTPException(
            status_code=429,
            detail={"error": "Превышен лимит запросов", "message": exc.message},
        )
    if isinstance(exc, ModelNotFoundError):
        return HTTPException(
            status_code=404,
            detail={"error": "Модель не найдена", "message": exc.message},
        )
    if isinstance(exc, BalanceError):
        return HTTPException(
            status_code=402,
            detail={"error": "Недостаточно средств", "message": exc.message},
        )
    if isinstance(exc, NetworkError):
        return HTTPException(
            status_code=503,
            detail={"error": "Ошибка сети", "message": exc.message},
        )
    if isinstance(exc, ProviderUnavailableError):
        return HTTPException(
            status_code=503,
            detail={"error": "Провайдер недоступен", "message": exc.message},
        )
    if isinstance(exc, InvalidRequestError):
        return HTTPException(
            status_code=400,
            detail={"error": "Неверный запрос", "message": exc.message},
        )
    return HTTPException(
        status_code=500,
        detail={"error": "Ошибка провайдера", "message": exc.message},
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest, http_request: Request):
    """Stream a chat completion from the active LLM provider."""
    provider = get_provider()
    if provider is None:
        raise HTTPException(status_code=503, detail="No provider configured")

    messages = list(request.messages)
    if request.system_prompt:
        from app.schemas import ChatMessage

        messages = [ChatMessage(role="system", content=request.system_prompt)] + messages

    if not request.use_context:
        messages = [message for message in messages if message.role == "system"] + [
            msg for msg in messages if msg.role == "user"
        ][-1:]

    request_to_send = request.model_copy(update={"messages": messages})

    logger.info(
        f"Messages to provider ({len(messages)}): "
        + str(
            [
                {
                    "role": message.role,
                    "content": (
                        message.content[:40]
                        if isinstance(message.content, str)
                        else f"[{len(message.content)} parts]"
                    ),
                }
                for message in messages
            ]
        )
    )

    stream = provider.chat(request_to_send)
    first_token: str | None = None

    try:
        first_token = await stream.__anext__()
    except StopAsyncIteration:
        first_token = None
    except ProviderError as exc:
        raise _provider_error_to_http(exc) from exc
    except Exception as exc:
        logger.error(f"Stream error before first token: {exc}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Ошибка провайдера", "message": str(exc)},
        ) from exc

    async def token_generator():
        if first_token is not None:
            if await http_request.is_disconnected():
                logger.info("Client disconnected before stream body")
                return
            yield first_token
        try:
            async for token in stream:
                if await http_request.is_disconnected():
                    logger.info("Client disconnected, stopping stream")
                    break
                yield token
        except ProviderError as exc:
            logger.error(f"Stream error after start: {exc}")
        except Exception as exc:
            logger.error(f"Unexpected stream error after start: {exc}")

    return StreamingResponse(token_generator(), media_type="text/plain; charset=utf-8")
