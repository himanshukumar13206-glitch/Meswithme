"""
Thin async MongoDB wrapper (motor) for:
- registered chats (for broadcast / stats)
- registered users
- play history / logging (also mirrored to the logger group)
- per-chat settings (e.g. auto-suggest on/off)
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from config import MONGO_DB_URI, DB_NAME

_client = AsyncIOMotorClient(MONGO_DB_URI)
db = _client[DB_NAME]

chats_col = db["chats"]
users_col = db["users"]
history_col = db["play_history"]
settings_col = db["chat_settings"]


async def add_served_chat(chat_id: int, title: str):
    await chats_col.update_one(
        {"_id": chat_id},
        {"$set": {"title": title, "last_active": datetime.now(timezone.utc)}},
        upsert=True,
    )


async def add_served_user(user_id: int, name: str):
    await users_col.update_one(
        {"_id": user_id},
        {"$set": {"name": name, "last_active": datetime.now(timezone.utc)}},
        upsert=True,
    )


async def get_all_served_chats():
    return [c["_id"] async for c in chats_col.find({}, {"_id": 1})]


async def get_all_served_users():
    return [u["_id"] async for u in users_col.find({}, {"_id": 1})]


async def log_play(chat_id: int, user_id: int, title: str, url: str, duration: str):
    await history_col.insert_one(
        {
            "chat_id": chat_id,
            "user_id": user_id,
            "title": title,
            "url": url,
            "duration": duration,
            "played_at": datetime.now(timezone.utc),
        }
    )


async def get_chat_setting(chat_id: int, key: str, default=None):
    doc = await settings_col.find_one({"_id": chat_id})
    if not doc:
        return default
    return doc.get(key, default)


async def set_chat_setting(chat_id: int, key: str, value):
    await settings_col.update_one(
        {"_id": chat_id}, {"$set": {key: value}}, upsert=True
    )
