import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_TG_ID", "0"))
HER_ID = int(os.getenv("HER_TG_ID", "0"))

TIMEZONE = "Europe/Moscow"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

if ADMIN_ID == 0:
    raise RuntimeError("ADMIN_TG_ID не найден в .env")

if HER_ID == 0:
    raise RuntimeError("HER_TG_ID не найден в .env")