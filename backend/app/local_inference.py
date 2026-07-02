"""Embedded local LLM inference via llama-cpp-python.

Runs GGUF models inside the backend process — no Ollama or external services.
"""

from __future__ import annotations

import asyncio
import os
import queue
import threading
from typing import AsyncIterator

from loguru import logger

from app.configs.local_models import get_model_info
from app.model_downloader import get_model_gguf_path
from app.schemas import ChatRequest

_engine_cache: dict[str, object] = {}
_engine_lock = asyncio.Lock()


def _resolve_n_gpu_layers(gpu_available: bool) -> int:
    env = os.environ.get("LOCAL_LLM_N_GPU_LAYERS")
    if env is not None:
        return int(env)
    return -1 if gpu_available else 0


def _build_messages(request: ChatRequest) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []

    if request.system_prompt:
        messages.append({"role": "system", "content": request.system_prompt})

    for msg in request.messages:
        if msg.role == "system":
            text = msg.content if isinstance(msg.content, str) else str(msg.content)
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] = text
            else:
                messages.insert(0, {"role": "system", "content": text})
        elif msg.role in ("user", "assistant"):
            if isinstance(msg.content, str):
                messages.append({"role": msg.role, "content": msg.content})
            else:
                text_parts = [p.text for p in msg.content if p.type == "text" and p.text]
                messages.append({"role": msg.role, "content": "\n".join(text_parts)})

    return messages


def _create_engine(model_id: str, gpu_available: bool):
    from llama_cpp import Llama

    gguf_path = get_model_gguf_path(model_id)
    if not gguf_path:
        raise FileNotFoundError(f"GGUF file not found for model {model_id}")

    model_info = get_model_info(model_id)
    n_ctx = min(model_info["context_length"] if model_info else 4096, 8192)
    n_gpu = _resolve_n_gpu_layers(gpu_available)

    logger.info(f"Loading local model {model_id} from {gguf_path} (n_ctx={n_ctx}, n_gpu_layers={n_gpu})")

    return Llama(
        model_path=str(gguf_path),
        n_ctx=n_ctx,
        n_gpu_layers=n_gpu,
        verbose=False,
    )


async def _get_engine(model_id: str, gpu_available: bool):
    async with _engine_lock:
        if model_id not in _engine_cache:
            if _engine_cache:
                _engine_cache.clear()
            _engine_cache[model_id] = await asyncio.to_thread(_create_engine, model_id, gpu_available)
        return _engine_cache[model_id]


def unload_engine(model_id: str | None = None) -> None:
    """Drop cached llama.cpp instances (e.g. after model delete)."""
    if model_id:
        _engine_cache.pop(model_id, None)
    else:
        _engine_cache.clear()


def _stream_tokens(llm, messages: list[dict], request: ChatRequest):
    stream = llm.create_chat_completion(
        messages=messages,
        stream=True,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
    )
    for chunk in stream:
        choices = chunk.get("choices") or []
        if not choices:
            continue
        delta = choices[0].get("delta") or {}
        token = delta.get("content")
        if token:
            yield token


def _producer(out_q: queue.Queue, llm, messages: list[dict], request: ChatRequest) -> None:
    try:
        for token in _stream_tokens(llm, messages, request):
            out_q.put(token)
    except Exception as exc:
        out_q.put(exc)
    finally:
        out_q.put(None)


async def stream_local_chat(
    model_id: str,
    request: ChatRequest,
    gpu_available: bool = False,
) -> AsyncIterator[str]:
    """Stream chat completion from an embedded GGUF model."""
    messages = _build_messages(request)
    if not any(m["role"] == "user" for m in messages):
        raise ValueError("No user message in request")

    llm = await _get_engine(model_id, gpu_available)
    out_q: queue.Queue = queue.Queue()
    thread = threading.Thread(
        target=_producer,
        args=(out_q, llm, messages, request),
        daemon=True,
    )
    thread.start()

    while True:
        item = await asyncio.to_thread(out_q.get)
        if item is None:
            break
        if isinstance(item, Exception):
            raise item
        yield item

    thread.join(timeout=1)
