from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.types import MediaStream

from clients import bot, call_py
from helpers.ytdl import search_youtube, resolve_stream
from helpers.queue import queue_manager, Track
from helpers.logger import log_play_event
from database.mongodb import log_play, add_served_chat
from config import DURATION_LIMIT_MIN


@bot.on_message(filters.command("play") & filters.group)
async def play(_, message: Message):
    chat_id = message.chat.id
    await add_served_chat(chat_id, message.chat.title)

    if len(message.command) < 2:
        await message.reply_text("Give me a song name or YouTube link.\nExample: <code>/play alan walker faded</code>")
        return

    query = message.text.split(None, 1)[1]
    status = await message.reply_text(f"🔎 Searching for <b>{query}</b> ...")

    is_url = query.startswith("http://") or query.startswith("https://")
    try:
        if is_url:
            candidate = {"url": query}
        else:
            results = await search_youtube(query)
            if not results:
                await status.edit_text("❌ No results found.")
                return
            candidate = results[0]

        resolved = await resolve_stream(candidate["url"])
    except Exception as e:
        await status.edit_text(f"❌ Couldn't fetch that track: <code>{e}</code>")
        return

    if resolved.get("duration_sec", 0) > DURATION_LIMIT_MIN * 60:
        await status.edit_text(f"❌ Track exceeds the {DURATION_LIMIT_MIN} minute limit set for this bot.")
        return

    track = Track(
        title=resolved["title"],
        url=candidate["url"],
        stream_url=resolved["stream_url"],
        duration=resolved["duration"],
        requested_by=message.from_user.id,
        thumbnail=resolved.get("thumbnail", ""),
    )

    already_playing = queue_manager.is_active(chat_id)
    queue_manager.add(chat_id, track)

    if not already_playing:
        try:
            await call_py.play(chat_id, MediaStream(track.stream_url))
        except Exception as e:
            queue_manager.clear(chat_id)
            await status.edit_text(
                f"❌ Couldn't join/stream in the VC: <code>{e}</code>\n"
                f"Make sure the assistant account is a member of this "
                f"group and a voice chat is active."
            )
            return
        await status.edit_text(f"▶️ <b>Now playing:</b> {track.title}\n⏱ {track.duration}")
    else:
        await status.edit_text(f"➕ <b>Queued:</b> {track.title}\n⏱ {track.duration}\nPosition: {len(queue_manager.get_queue(chat_id))}")

    await log_play(chat_id, message.from_user.id, track.title, track.url, track.duration)
    await log_play_event(message.chat.title, chat_id, message.from_user.mention, track.title, track.url, track.duration)


@bot.on_message(filters.command("queue") & filters.group)
async def show_queue(_, message: Message):
    q = queue_manager.get_queue(message.chat.id)
    if not q:
        await message.reply_text("Queue is empty.")
        return
    lines = [f"{i}. {t.title} ({t.duration})" for i, t in enumerate(q, start=1)]
    await message.reply_text("🎵 <b>Queue</b>\n" + "\n".join(lines))
