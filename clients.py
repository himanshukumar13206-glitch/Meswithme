"""
Two Telegram sessions are required for a VC music bot:

1. `bot`      — a normal Bot API account (BOT_TOKEN). Handles commands,
                buttons, sends messages. Bots CANNOT join voice chats.
2. `assistant`— a real user account logged in via SESSION_STRING. This
                is what PyTgCalls uses to actually join the group's
                voice chat and stream audio into it.

Add the assistant account to your groups (or let it auto-join via
invite link) — it must be a member to join the VC.
"""

from pyrogram import Client
from pytgcalls import PyTgCalls

from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

# Bot session (uses bot token)
bot = Client(
    "@Meowwww_xbot",          # session name (string)
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,           # don't save session file locally
)

# Assistant user session (uses session string for voice chat)
assistant = Client(
    "meow_assistant",         # session name (string)
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    in_memory=True,
)

call_py = PyTgCalls(assistant)  # PyTgCalls uses the assistant to join VCs
