
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TOKEN")
DEVELOPER_CHAT_ID = os.environ.get("SUDO")
MAINTAINERS_CHAT_IDS = [
    DEVELOPER_CHAT_ID,
]

SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "/tmp/users.db")
