"""Tests for ChatRepository."""

import pytest

from app.repositories.chat_repository import ChatRepository


@pytest.fixture
async def temp_db(patch_db_path):
    """Create a temporary database for testing."""
    path = patch_db_path

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


@pytest.mark.asyncio
async def test_chat_repository_save(temp_db):
    """Test saving a chat."""
    chat_id = "test-chat-1"
    title = "Test Chat"

    await ChatRepository.save(chat_id, title, temp_db)

    chats = await ChatRepository.get_list(temp_db)
    assert len(chats) == 1
    assert chats[0]['id'] == chat_id
    assert chats[0]['title'] == title


@pytest.mark.asyncio
async def test_chat_repository_update(temp_db):
    """Test updating an existing chat."""
    chat_id = "test-chat-2"

    await ChatRepository.save(chat_id, "Original Title", temp_db)
    await ChatRepository.save(chat_id, "Updated Title", temp_db)

    chats = await ChatRepository.get_list(temp_db)
    assert chats[0]['title'] == "Updated Title"


@pytest.mark.asyncio
async def test_chat_repository_delete(temp_db):
    """Test deleting a chat."""
    chat_id = "test-chat-3"

    await ChatRepository.save(chat_id, "To Delete", temp_db)
    deleted = await ChatRepository.delete(chat_id, temp_db)

    assert deleted is True

    chats = await ChatRepository.get_list(temp_db)
    assert len(chats) == 0


@pytest.mark.asyncio
async def test_chat_repository_reorder(temp_db):
    """Test reordering chats."""
    await ChatRepository.save("chat-1", "First", temp_db)
    await ChatRepository.save("chat-2", "Second", temp_db)
    await ChatRepository.save("chat-3", "Third", temp_db)

    await ChatRepository.reorder(["chat-3", "chat-1", "chat-2"], temp_db)

    chats = await ChatRepository.get_list(temp_db)
    assert [c['id'] for c in chats] == ["chat-3", "chat-1", "chat-2"]


@pytest.mark.asyncio
async def test_chat_repository_count(temp_db):
    """Test getting chat count."""
    await ChatRepository.save("chat-1", "One", temp_db)
    await ChatRepository.save("chat-2", "Two", temp_db)

    count = await ChatRepository.get_count(temp_db)
    assert count == 2
