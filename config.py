import os
from dotenv import load_dotenv

load_dotenv()


def _int(name, default=0):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


API_ID = _int("API_ID")
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = _int("OWNER_ID")

SESSION_STRING = os.getenv("SESSION_STRING", "")

MONGO_DB_URI = os.getenv("MONGO_DB_URI", "")
DB_NAME = os.getenv("DB_NAME", "meow_music")

LOGGER_GROUP_ID = _int("LOGGER_GROUP_ID")

DURATION_LIMIT_MIN = _int("DURATION_LIMIT_MIN", 60)
AUTO_LEAVE_MIN = _int("AUTO_LEAVE_MIN", 5)

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# === Branding / links shown on /start ===
START_IMG_URL = os.getenv(
    "START_IMG_URL",
    "https://telegra.ph/file/example-placeholder.jpg",  # replace with your own image URL
)
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/your_channel")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/your_support_group")
# Mini App URL — must be https and registered with @BotFather via
# /newapp or /setmenubutton before the WebApp button will work.
MINI_APP_URL = os.getenv("MINI_APP_URL", "")

# sanity checks so the bot fails loudly instead of mysteriously
_required = {
    "API_ID": API_ID,
    "API_HASH": API_HASH,
    "BOT_TOKEN": BOT_TOKEN,
    "SESSION_STRING": SESSION_STRING,
    "MONGO_DB_URI": MONGO_DB_URI,
}
missing = [k for k, v in _required.items() if not v]
if missing:
    raise SystemExit(
        f"Missing required .env values: {', '.join(missing)}. "
        f"Copy .env.example to .env and fill it in."
    )
