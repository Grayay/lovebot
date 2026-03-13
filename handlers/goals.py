from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import SessionLocal
from models.goals import Goal
from services.eventlog import log_event

router = Router()


class GoalState(StatesGroup):
    waiting_for_goal = State()


@router.message(F.text == "🎯 Наши цели")
async def goal_start(message: Message, state: FSMContext):
    await state.set_state(GoalState.waiting_for_goal)
    await message.answer("Напиши новую цель")


@router.message(GoalState.waiting_for_goal)
async def goal_create(message: Message, state: FSMContext):
    async with SessionLocal() as session:
        session.add(Goal(author=message.from_user.id, title=message.text))
        await session.commit()

    await message.answer("Цель сохранена 🎯")
    await state.clear()
await log_event(
    actor=message.from_user.id,
    module="goals",
    event_type="goal_created",
    after=message.text
)