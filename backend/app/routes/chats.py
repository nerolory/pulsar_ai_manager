from fastapi import APIRouter, HTTPException, Query
from app.database import save_chat, add_message, update_message_content, get_chat_list, get_chat_messages, clear_chat_messages, reorder_chats, delete_chat, get_chat_count
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger

router = APIRouter(prefix="/chats")

class ChatResponse(BaseModel):
    id: str
    title: str
    createdAt: int
    updatedAt: int

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    createdAt: int
    model: Optional[str] = None

class ChatCreateRequest(BaseModel):
    title: str
    id: Optional[str] = None

class MessageSchema(BaseModel):
    id: str
    role: str
    content: str
    createdAt: int
    model: Optional[str] = None

class ChatUpdateRequest(BaseModel):
    id: str
    title: str
    messages: List[MessageSchema]

class ChatRenameRequest(BaseModel):
    title: str

class ReorderRequest(BaseModel):
    ids: List[str]

class AddMessageRequest(BaseModel):
    id: str
    role: str
    content: str
    createdAt: int
    model: Optional[str] = None

@router.get("", response_model=List[ChatResponse])
async def list_chats():
    """Get all chats ordered by last update"""
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
    """Save new chat order"""
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
    """Get messages for a chat with pagination support"""
    try:
        messages = await get_chat_messages(chat_id, limit=limit, before_rowid=before)
        response = [
            MessageResponse(
                id=msg["id"],
                role=msg["role"],
                content=msg["content"],
                createdAt=msg["created_at"],
                model=msg.get("model")
            )
            for msg in messages
        ]
        logger.debug(f"[get_messages] chat={chat_id} count={len(response)} order={[(m.role, m.createdAt) for m in response]}")
        return response
    except Exception as e:
        logger.error(f"Failed to get messages for chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load messages")

@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def add_message_endpoint(chat_id: str, request: AddMessageRequest):
    """Add a single message to a chat"""
    try:
        await add_message(chat_id, request.id, request.role, request.content, request.createdAt, request.model)
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
    """Create a new empty chat"""
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
    """Update chat title and save messages"""
    try:
        # Convert messages to dict format
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
    """Rename a chat"""
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
    """Delete all messages in a chat without deleting the chat"""
    try:
        await clear_chat_messages(chat_id)
        return {"cleared": True}
    except Exception as e:
        logger.error(f"Failed to clear messages for chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear messages")

@router.delete("/{chat_id}")
async def delete_chat_endpoint(chat_id: str):
    """Delete a chat and all its messages"""
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
    """Get statistics about chats"""
    try:
        count = await get_chat_count()
        return {"total_chats": count}
    except Exception as e:
        logger.error(f"Failed to get chat stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")
