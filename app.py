import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN
from database import engine, Base
from keyboards.main_menu import main_menu

from handlers.mood import router as mood_router
from handlers.miss import router as miss_router
from handlers.goals import router as goals_router
from handlers.plans import router as plans_router
from handlers.shopping import router as shopping_router
from handlers.expenses import router as expenses_router
from handlers.discussions import router as discussions_router
from handlers.memories import router as memories_router
from handlers.dates import router as dates_router
from handlers.wishlist import router as wishlist_router
from handlers.gift import router as gift_router

from models import (
    mood,
    goals,
    plans,
    shopping,
    expenses,
    wishlist,
    discussions,
    memories,
    dates,
    eventlog,
    settings,
)

from services.scheduler import start_scheduler, stop_scheduler
from services.notifications import seed_home_products


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать 💜",
        reply_markup=main_menu
    )


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def register_routers():
    dp.include_router(mood_router)
    dp.include_router(miss_router)
    dp.include_router(goals_router)
    dp.include_router(plans_router)
    dp.include_router(shopping_router)
    dp.include_router(expenses_router)
    dp.include_router(discussions_router)
    dp.include_router(memories_router)
    dp.include_router(dates_router)
    dp.include_router(wishlist_router)
    dp.include_router(gift_router)


async def main():
    await create_tables()
    await seed_home_products()
    register_routers()

    await bot.delete_webhook(drop_pending_updates=True)

    scheduler = await start_scheduler(bot)

    try:
        await dp.start_polling(bot)
    finally:
        await stop_scheduler(scheduler)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())