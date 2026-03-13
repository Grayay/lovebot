from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.inline import mood_keyboard
from database import SessionLocal
from models.mood import MoodEntry
from config import ADMIN_ID, HER_ID
from services.eventlog import log_event

router = Router()


@router.message(F.text == "🩺 Самочувствие")
async def mood_start(message: Message):
    await message.answer("Какое сейчас самочувствие?", reply_markup=mood_keyboard())


@router.callback_query(F.data.startswith("mood_"))
async def mood_selected(callback: CallbackQuery):
    score = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    async with SessionLocal() as session:
        session.add(MoodEntry(author_id=user_id, score=score))
        await session.commit()

    await callback.message.edit_text("Спасибо 💜\nСамочувствие записано.")

    if user_id == HER_ID:
        await callback.bot.send_message(ADMIN_ID, f"💛 Самочувствие: {score}/10")

    await callback.answer()

    await log_event(
        actor=user_id,
        module="mood",
        event_type="mood_logged",
        after=str(score)
    )