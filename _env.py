import os

from pathlib import Path

BASE_DIR = Path(__file__).parent

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    with open(BASE_DIR / "TOKEN") as f:
        TOKEN = f.read().strip()

if not TOKEN:
    raise KeyError("No TOKEN found!")

PRODUCTION_MODE = bool(os.environ.get("TELEGRAM_BOT_PRODUCTION", default=False))
