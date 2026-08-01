# Meow ⌁ Music — Telegram VC Music Bot (starter)

A working skeleton for a Telegram voice-chat music bot:
**Pyrogram** (bot commands) + **PyTgCalls** (VC streaming) + **yt-dlp**
(search & audio, no YouTube API key/quota) + **MongoDB** (persistence)
+ a logger group.

## How it fits together

- `bot` — the Bot API account users talk to (`/play`, `/skip`, etc.)
- `assistant` — a **real user account** (via a Pyrogram session string)
  that actually joins the group voice chat and streams audio.
  Bots cannot join voice chats — this is a hard Telegram limitation,
  every VC music bot uses an assistant/userbot account for this.
- `call_py` (PyTgCalls) — bridges the assistant into the VC and pipes
  the yt-dlp-resolved audio stream into it.
- MongoDB — served chats/users, play history, per-chat settings.
- Logger group — the bot posts new-chat / play events there.

## Setup

1. **Get API_ID / API_HASH**: https://my.telegram.org → API Development Tools
2. **Create the bot**: message @BotFather → `/newbot` → copy the token
3. **Generate a session string for the assistant account**:
   ```bash
   pip install pyrogram tgcrypto
   python3 -c "
   from pyrogram import Client
   with Client('gen', api_id=YOUR_API_ID, api_hash='YOUR_API_HASH') as app:
       print(app.export_session_string())
   "
   ```
   Log in with the account you want to use as the VC assistant (not
   the bot). This account needs to be a **member** of every group it
   plays music in.
4. **Install FFmpeg** (required by PyTgCalls to transcode audio):
   `apt install ffmpeg` (Linux) / `brew install ffmpeg` (Mac)
5. **Set up MongoDB**: free tier at https://mongodb.com/atlas works fine
6. **Create a logger group**, add both the bot and the assistant as
   admins, get its ID (forward a message from it to @userinfobot, or
   use @RawDataBot), put it in `.env` as a negative number.
7. Copy `.env.example` → `.env` and fill in every value.
8. ```bash
   pip install -r requirements.txt
   python3 main.py
   ```

## Commands included

`/start` `/help` `/play` `/queue` `/pause` `/resume` `/skip` `/end`

## What I built vs. what you still need to add

**Included (working core):**
- Search + stream resolution via yt-dlp (no API key/quota)
- Join VC, stream, queue, skip, pause/resume, auto-advance on track end
- MongoDB models for served chats/users and play history
- Logger group integration
- `.env`-based config with startup validation

**You'll want to add before calling this "perfect":**
1. **Auth/permissions** — right now anyone in a group can control
   playback. Add an admin-only filter (Pyrogram `filters.create`
   checking `get_chat_member`) for `/skip`, `/end`, `/pause` if you
   don't want random members pausing music.
2. **Auto song suggestions** ("Meow" mentioned this) — after a track
   ends with an empty queue, pull YouTube's related-video list for the
   last track (yt-dlp exposes this) and auto-queue one.
3. **Cookies for yt-dlp** — YouTube periodically throws bot-check
   errors on datacenter IPs. Export `cookies.txt` from a logged-in
   browser (see commented-out line in `helpers/ytdl.py`) and it fixes
   most of it. This is the #1 thing that breaks these bots in prod.
4. **Multiple assistant accounts** — one assistant can only be in one
   VC per chat at a time but is fine for many chats simultaneously;
   if you scale to hundreds of groups, add an assistant pool and
   round-robin chat_id → assistant.
5. **Rate limiting / flood control** — wrap `/play` with a per-user
   cooldown so people can't spam-queue.
6. **Broadcast command** — you already have `get_all_served_chats()` /
   `get_all_served_users()` in the DB layer; wire up an owner-only
   `/broadcast` command using them.
7. **Inline search results** — instead of always taking the first
   yt-dlp result, show the top 5 with inline buttons so users pick.
8. **Deploy** — a VPS (Hetzner/Contabo are the usual budget picks for
   this kind of bot) with `pm2` or a `systemd` service, since these
   bots need to run 24/7 and FFmpeg/PyTgCalls don't play nice with
   most serverless platforms.
9. **Docker** — containerize with ffmpeg baked into the image if you
   want reproducible deploys.

## Notes on the projects you linked

- `yt-search-python` is a lighter-weight search-only wrapper; I used
  `yt-dlp` directly instead since it also resolves the direct stream
  URL in one call and is more actively maintained against YouTube's
  changes — but you can swap `helpers/ytdl.py`'s search function for
  it if you prefer its output format.
- Bots like "Meow ⌁ Music" are almost certainly built on this exact
  stack (Pyrogram + PyTgCalls + yt-dlp/youtube-dl + Mongo) — there's
  no special trick, it's this architecture plus a lot of polish on
  #1–8 above.
