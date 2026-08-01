"""
Per-chat queue. Kept in memory (dict) for speed — queues are ephemeral,
they don't need to survive a restart. If you want persistence across
restarts, mirror push/pop into Mongo too.
"""

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Track:
    title: str
    url: str            # original YouTube URL
    stream_url: str      # direct audio stream URL resolved by yt-dlp
    duration: str
    requested_by: int
    thumbnail: str = ""


class QueueManager:
    def __init__(self):
        self._queues: dict[int, list[Track]] = defaultdict(list)

    def add(self, chat_id: int, track: Track):
        self._queues[chat_id].append(track)

    def current(self, chat_id: int) -> Track | None:
        q = self._queues.get(chat_id)
        return q[0] if q else None

    def pop_next(self, chat_id: int) -> Track | None:
        q = self._queues.get(chat_id)
        if not q:
            return None
        q.pop(0)
        return q[0] if q else None

    def get_queue(self, chat_id: int) -> list[Track]:
        return self._queues.get(chat_id, [])

    def clear(self, chat_id: int):
        self._queues[chat_id] = []

    def is_active(self, chat_id: int) -> bool:
        return bool(self._queues.get(chat_id))


queue_manager = QueueManager()
