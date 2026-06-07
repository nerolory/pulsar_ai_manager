"""Chat streaming route for LLM completions.

Handles streaming chat requests to the active LLM provider, including
system prompt injection and context window management.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest
from app.state import get_provider
from loguru import logger

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream a chat completion from the active LLM provider.

    Injects the system prompt if provided and trims the context
    when context mode is disabled.

    Args:
        request: ChatRequest with messages, temperature, max_tokens and flags.

    Returns:
        StreamingResponse: Plain-text stream of generated tokens.

    Raises:
        HTTPException: If no provider is configured.
    """
    provider = get_provider()
    if provider is None:
        raise HTTPException(status_code=503, detail="No provider configured")

    # Prepend system prompt if provided
    messages = list(request.messages)
    if request.system_prompt:
        from app.schemas import ChatMessage

        messages = [ChatMessage(role="system", content=request.system_prompt)] + messages

    # If context disabled — only keep last user message
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

    async def token_generator():
        """Yield tokens from the provider, catching errors gracefully."""
        try:
            async for token in provider.chat(request_to_send):
                yield token
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"\n\n[Ошибка: {e}]"

    return StreamingResponse(token_generator(), media_type="text/plain; charset=utf-8")
