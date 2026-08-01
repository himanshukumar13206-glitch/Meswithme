"""
YouTube search + direct-audio-stream resolution using yt-dlp.
No API key, no quota — works by scraping like youtube-dl always has.

NOTE: If YouTube starts throwing "Sign in to confirm you're not a bot"
errors, export cookies.txt from a logged-in browser session and set
cookiefile below. This is the #1 cause of these bots breaking in prod.
"""

import asyncio
import yt_dlp

YDL_SEARCH_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch5",
    "noplaylist": True,
    "skip_download": True,
    # "cookiefile": "cookies.txt",   # uncomment if you hit bot-check errors
}

YDL_STREAM_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "format": "bestaudio/best",
    "noplaylist": True,
    "skip_download": True,
    "geo_bypass": True,
    # "cookiefile": "cookies.txt",
}


def _search_sync(query: str) -> list[dict]:
    with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        entries = info.get("entries", [info])
        results = []
        for e in entries:
            if not e:
                continue
            results.append(
                {
                    "title": e.get("title", "Unknown"),
                    "url": f"https://www.youtube.com/watch?v={e.get('id')}",
                    "duration": _fmt_duration(e.get("duration")),
                    "thumbnail": (e.get("thumbnails") or [{}])[-1].get("url", ""),
                    "channel": e.get("uploader", "Unknown"),
                }
            )
        return results


def _stream_url_sync(url: str) -> dict:
    with yt_dlp.YoutubeDL(YDL_STREAM_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", "Unknown"),
            "stream_url": info.get("url"),
            "duration": _fmt_duration(info.get("duration")),
            "duration_sec": info.get("duration", 0),
            "thumbnail": (info.get("thumbnails") or [{}])[-1].get("url", ""),
        }


def _fmt_duration(seconds):
    if not seconds:
        return "Live/Unknown"
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"


async def search_youtube(query: str) -> list[dict]:
    """Returns up to 5 candidate results for a text query."""
    return await asyncio.to_thread(_search_sync, query)


async def resolve_stream(url: str) -> dict:
    """Given a YouTube URL, resolve a direct playable audio stream URL."""
    return await asyncio.to_thread(_stream_url_sync, url)
