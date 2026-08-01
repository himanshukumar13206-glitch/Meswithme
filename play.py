from pyrogram import filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from clients import bot
from database.mongodb import add_served_chat, add_served_user
from helpers.logger import log_new_chat
from config import START_IMG_URL, SUPPORT_CHANNEL, SUPPORT_GROUP, MINI_APP_URL

START_CAPTION = (
    "👋 <b>Hey, I'm Meow ⌁ Music!</b>\n\n"
    "Click the buttons below to get information about my commands.\n\n"
    "<i>Note: All commands can be used with /</i>"
)

HELP_TEXT = (
    "<b>Commands</b>\n"
    "/play <name|url> — search & play/queue a track\n"
    "/pause — pause playback\n"
    "/resume — resume playback\n"
    "/skip — skip to next in queue\n"
    "/end — stop and clear queue, leave VC\n"
    "/queue — show current queue\n"
    "/ping — check bot status"
)


def _start_buttons(bot_username: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                "➕ Add me to your group",
                url=f"https://t.me/{bot_username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="show_help"),
        ],
        [
            InlineKeyboardButton("📢 Support Channel", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("💬 Support VC", url=SUPPORT_GROUP),
        ],
    ]
    # Only show the Mini App button once MINI_APP_URL is actually configured
    # (an empty/invalid WebAppInfo url makes Telegram reject the button).
    if MINI_APP_URL:
        rows.append(
            [InlineKeyboardButton("🎛 Open App", web_app=WebAppInfo(url=MINI_APP_URL))]
        )
    return InlineKeyboardMarkup(rows)


@bot.on_message(filters.command("start") & filters.private)
async def start_private(_, message: Message):
    await add_served_user(message.from_user.id, message.from_user.first_name)
    me = await bot.get_me()
    await message.reply_photo(
        photo=START_IMG_URL,
        caption=START_CAPTION,
        reply_markup=_start_buttons(me.username),
    )


@bot.on_message(filters.command("start") & filters.group)
async def start_group(_, message: Message):
    await add_served_chat(message.chat.id, message.chat.title)
    await message.reply_text("I'm alive. Use /play <song name> to start streaming in the VC.")


@bot.on_message(filters.command("help"))
async def help_cmd(_, message: Message):
    await message.reply_text(HELP_TEXT)


@bot.on_callback_query(filters.regex("^show_help$"))
async def help_callback(_, cq: CallbackQuery):
    await cq.answer()
    await cq.message.reply_text(HELP_TEXT)


@bot.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start_callback(_, cq: CallbackQuery):
    await cq.answer()
    me = await bot.get_me()
    await cq.message.edit_caption(caption=START_CAPTION, reply_markup=_start_buttons(me.username))


@bot.on_message(filters.new_chat_members)
async def on_added(_, message: Message):
    me = await bot.get_me()
    for member in message.new_chat_members:
        if member.id == me.id:
            await add_served_chat(message.chat.id, message.chat.title)
            await log_new_chat(message.chat.title, message.chat.id)
