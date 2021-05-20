
import os

# this is the bot token, gotten from BotFather
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
# this is your own telegram ID, which is used to send exception tracebacks
DEVELOPER_CHAT_ID = os.environ["DEVELOPER_CHAT_ID"]
# list of telegram IDs for them /stats command is enabled
MAINTAINERS_CHAT_IDS = [
    DEVELOPER_CHAT_ID,
]

SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "/tmp/users.db")
