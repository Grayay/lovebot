from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import SessionLocal
from models.dateideas import DateIdea
from services.eventlog import log_event

router = Router()


class IdeaState(StatesGroup):
    waiting_idea = State()


@router.message(F.text == "✨ Идеи свиданий")
async def idea_start(message: Message, state: FSMContext):
    await state.set_state(IdeaState.waiting_idea)
    await message.answer("Напиши идею свидания")


@router.message(IdeaState.waiting_idea)
async def idea_create(message: Message, state: FSMContext):

    async with SessionLocal() as session:
        session.add(
            DateIdea(
                author=message.from_user.id,
                title=message.text
            )
        )
        await session.commit()

    await message.answer("Идея сохранена ✨")
    await state.clear()
await log_event(
    actor=message.from_user.id,
    module="dates",
    event_type="idea_added",
    after=message.text
)