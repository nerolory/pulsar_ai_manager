"""Chat CRUD routes for managing conversations and messages.

Provides endpoints for creating, reading, updating and deleting chats,
adding messages, reordering conversations, and pagination support.
"""

from fastapi import APIRouter, HTTPException, Query
from app.database import save_chat, add_message, update_message_content, get_chat_list, get_chat_messages, clear_chat_messages, reorder_chats, delete_chat, get_chat_count
from pydantic import BaseModel
from typing import List, Optional, Union
from loguru import logger
import json

router = APIRouter(prefix="/chats")


class ChatResponse(BaseModel):
    """Serialised chat summary returned to the client."""
    id: str
    title: str
    createdAt: int
    updatedAt: int


class MessageResponse(BaseModel):
    """Serialised chat message returned to the client."""
    id: str
    role: str
    content: Union[str, list]
    createdAt: int
    model: Optional[str] = None


class ChatCreateRequest(BaseModel):
    """Payload for creating a new chat."""
    title: str
    id: Optional[str] = None


class MessageSchema(BaseModel):
    """Internal schema representing a single chat message."""
    id: str
    role: str
    content: Union[str, list]
    createdAt: int
    model: Optional[str] = None


def serialize_content(content: Union[str, list]) -> str:
    """Convert message content to a JSON string if it is a list.

    Args:
        content: Raw content, either a plain string or a list of parts.

    Returns:
        str: JSON-encoded list or the original string.
    """
    if isinstance(content, list):
        return json.dumps(content, ensure_ascii=False)
    return content


def deserialize_content(content: str) -> Union[str, list]:
    """Convert a stored JSON string back to a list when applicable.

    Args:
        content: Raw stored string.

    Returns:
        Union[str, list]: Parsed list or the original string.
    """
    if content and content.startswith('['):
        try:
            return json.loads(content)
        except Exception:
            pass
    return content


class ChatUpdateRequest(BaseModel):
    """Payload for updating an existing chat with new messages."""
    id: str
    title: str
    messages: List[MessageSchema]


class ChatRenameRequest(BaseModel):
    """Payload for renaming a chat."""
    title: str


class ReorderRequest(BaseModel):
    """Payload for reordering the chat list."""
    ids: List[str]


class AddMessageRequest(BaseModel):
    """Payload for adding a single message to a chat."""
    id: str
    role: str
    content: Union[str, list]
    createdAt: int
    model: Optional[str] = None


@router.get("", response_model=List[ChatResponse])
async def list_chats():
    """Return all chats ordered by last update time.

    Returns:
        List[ChatResponse]: List of chat summaries.

    Raises:
        HTTPException: On database errors.
    """
    try:
        chats = await get_chat_list()
        return [
            ChatResponse(
                id=chat["id"],
                title=chat["title"],
                createdAt=chat["created_at"],
                updatedAt=chat["updated_at"]
            )
            for chat in chats
        ]
    except Exception as e:
        logger.error(f"Failed to list chats: {e}")
        raise HTTPException(status_code=500, detail="Failed to load chats")


@router.post("/reorder")
async def reorder_chats_endpoint(request: ReorderRequest):
    """Persist a new custom order for the chat list.

    Args:
        request: ReorderRequest containing the ordered list of chat IDs.

    Returns:
        dict: Confirmation object.
    """
    try:
        await reorder_chats(request.ids)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to reorder chats: {e}")
        raise HTTPException(status_code=500, detail="Failed to reorder chats")


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    chat_id: str,
    limit: Optional[int] = Query(10, description="Number of messages to load"),
    before: Optional[int] = Query(None, description="Load messages before this rowid")
):
    """Retrieve paginated messages for a specific chat.

    Args:
        chat_id: Unique identifier of the chat.
        limit: Maximum number of messages to return.
        before: Optional rowid cursor for pagination.

    Returns:
        List[MessageResponse]: Messages in chronological order.
    """
    try:
        messages = await get_chat_messages(chat_id, limit=limit, before_rowid=before)
        response = [
            MessageResponse(
                id=message["id"],
                role=message["role"],
                content=deserialize_content(message["content"]),
                createdAt=message["created_at"],
                model=message.get("model")
            )
            for message in messages
        ]
        logger.debug(f"[get_messages] chat={chat_id} count={len(response)} order={[(msg.role, msg.createdAt) for msg in response]}")
        return response
    except Exception as e:
        logger.error(f"Failed to get messages for chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load messages")


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def add_message_endpoint(chat_id: str, request: AddMessageRequest):
    """Append a single message to the specified chat.

    Args:
        chat_id: Target chat identifier.
        request: AddMessageRequest with message details.

    Returns:
        MessageResponse: The added message.
    """
    try:
        await add_message(chat_id, request.id, request.role, serialize_content(request.content), request.createdAt, request.model)
        return MessageResponse(
            id=request.id,
            role=request.role,
            content=request.content,
            createdAt=request.createdAt,
            model=request.model
        )
    except Exception as e:
        logger.error(f"Failed to add message to chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add message")


@router.post("", response_model=ChatResponse)
async def create_chat(request: ChatCreateRequest):
    """Create a new empty chat with a generated UUID.

    Args:
        request: ChatCreateRequest with optional pre-defined id and title.

    Returns:
        ChatResponse: The newly created chat summary.
    """
    try:
        import uuid
        from datetime import datetime
        chat_id = request.id or str(uuid.uuid4())
        now = int(datetime.now().timestamp() * 1000)
        await save_chat(chat_id, request.title, [])
        return ChatResponse(
            id=chat_id,
            title=request.title,
            createdAt=now,
            updatedAt=now
        )
    except Exception as e:
        logger.error(f"Failed to create chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat")


@router.put("/{chat_id}", response_model=ChatResponse)
async def update_chat(chat_id: str, request: ChatUpdateRequest):
    """Overwrite a chat title and its entire message history.

    Args:
        chat_id: Chat identifier.
        request: ChatUpdateRequest with title and full message list.

    Returns:
        ChatResponse: Updated chat summary.
    """
    try:
        messages_dict = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "createdAt": msg.createdAt,
                "model": msg.model
            }
            for msg in request.messages
        ]
        await save_chat(chat_id, request.title, messages_dict)
        from datetime import datetime
        now = int(datetime.now().timestamp() * 1000)
        return ChatResponse(
            id=chat_id,
            title=request.title,
            createdAt=request.messages[0].createdAt if request.messages else now,
            updatedAt=now
        )
    except Exception as e:
        logger.error(f"Failed to update chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save chat")


@router.patch("/{chat_id}", response_model=ChatResponse)
async def rename_chat(chat_id: str, request: ChatRenameRequest):
    """Rename an existing chat without touching its messages.

    Args:
        chat_id: Chat identifier.
        request: ChatRenameRequest with the new title.

    Returns:
        ChatResponse: Updated chat summary.
    """
    try:
        await save_chat(chat_id, request.title)
        from datetime import datetime
        now = int(datetime.now().timestamp() * 1000)
        return ChatResponse(id=chat_id, title=request.title, createdAt=now, updatedAt=now)
    except Exception as e:
        logger.error(f"Failed to rename chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to rename chat")


@router.delete("/{chat_id}/messages")
async def clear_messages_endpoint(chat_id: str):
    """Remove all messages from a chat while keeping the chat itself.

    Args:
        chat_id: Chat identifier.

    Returns:
        dict: Confirmation object.
    """
    try:
        await clear_chat_messages(chat_id)
        return {"cleared": True}
    except Exception as e:
        logger.error(f"Failed to clear messages for chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear messages")


@router.delete("/{chat_id}")
async def delete_chat_endpoint(chat_id: str):
    """Permanently delete a chat and all of its messages.

    Args:
        chat_id: Chat identifier.

    Returns:
        dict: Confirmation object.

    Raises:
        HTTPException: 404 if the chat does not exist.
    """
    try:
        deleted = await delete_chat(chat_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat")


@router.get("/count")
async def get_chat_stats():
    """Return the total number of stored chats.

    Returns:
        dict: Object containing the chat count.
    """
    try:
        count = await get_chat_count()
        return {"total_chats": count}
    except Exception as e:
        logger.error(f"Failed to get chat stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")
