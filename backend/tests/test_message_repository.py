"""Tests for MessageRepository."""

import asyncio
import tempfile
import os
from pathlib import Path

import pytest

from app.repositories.message_repository import MessageRepository
from app.repositories.chat_repository import ChatRepository


@pytest.fixture
async def temp_db(monkeypatch):
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    import app.paths
    monkeypatch.setattr(app.paths, 'DB_PATH', Path(path))
    
    import aiosqlite
    async with aiosqlite.connect(path) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                sort_order INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                model TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            );
        """)
        await db.commit()
    
    yield path
    
    os.unlink(path)


@pytest.mark.asyncio
async def test_message_repository_add(temp_db):
    """Test adding a message to a chat."""
    chat_id = "test-chat-1"
    msg_id = "msg-1"
    
    await ChatRepository.save(chat_id, "Test Chat", Path(temp_db))
    await MessageRepository.add(chat_id, msg_id, "user", "Hello", 1234567890, None, Path(temp_db))
    
    messages = await MessageRepository.get_by_chat(chat_id, db_path=Path(temp_db))
    assert len(messages) == 1
    assert messages[0]['id'] == msg_id
    assert messages[0]['role'] == "user"


@pytest.mark.asyncio
async def test_message_repository_update_content(temp_db):
    """Test updating message content."""
    chat_id = "test-chat-2"
    msg_id = "msg-2"
    
    await ChatRepository.save(chat_id, "Test Chat", Path(temp_db))
    await MessageRepository.add(chat_id, msg_id, "user", "Original", 1234567890, None, Path(temp_db))
    await MessageRepository.update_content(msg_id, "Updated", Path(temp_db))
    
    messages = await MessageRepository.get_by_chat(chat_id, db_path=Path(temp_db))
    assert messages[0]['content'] == "Updated"


@pytest.mark.asyncio
async def test_message_repository_pagination(temp_db):
    """Test message pagination with before_rowid."""
    chat_id = "test-chat-3"
    
    await ChatRepository.save(chat_id, "Test Chat", Path(temp_db))
    
    # Add 5 messages
    for i in range(5):
        await MessageRepository.add(chat_id, f"msg-{i}", "user", f"Message {i}", 1234567890 + i, None, Path(temp_db))
    
    # Get last 2 messages
    messages = await MessageRepository.get_by_chat(chat_id, limit=2, db_path=Path(temp_db))
    assert len(messages) == 2
    assert messages[0]['id'] == "msg-3"
    assert messages[1]['id'] == "msg-4"


@pytest.mark.asyncio
async def test_message_repository_clear_by_chat(temp_db):
    """Test clearing all messages for a chat."""
    chat_id = "test-chat-4"
    
    await ChatRepository.save(chat_id, "Test Chat", Path(temp_db))
    await MessageRepository.add(chat_id, "msg-1", "user", "Hello", 1234567890, None, Path(temp_db))
    await MessageRepository.add(chat_id, "msg-2", "assistant", "Hi", 1234567891, None, Path(temp_db))
    
    await MessageRepository.clear_by_chat(chat_id, Path(temp_db))
    
    messages = await MessageRepository.get_by_chat(chat_id, db_path=Path(temp_db))
    assert len(messages) == 0
