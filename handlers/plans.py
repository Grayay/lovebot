from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database import SessionLocal
from models.plans import Plan
from datetime import datetime, timedelta

from keyboards.inline import list_keyboard, add_only_keyboard

router = Router()

PLANS_PREFIX = "plans"


class PlanState(StatesGroup):
    waiting_for_title = State()
    waiting_for_edit = State()


def _format_plan(plan: Plan) -> str:
    dt_str = plan.dt_start.strftime("%d.%m %H:%M") if plan.dt_start else "—"
    return f"• {plan.title} ({dt_str})"


async def _get_plans_list(session) -> list[Plan]:
    result = await session.execute(select(Plan).order_by(Plan.dt_start))
    return list(result.scalars().all())


@router.message(F.text == "💛 Наши планы")
async def plan_list(message: Message):
    async with SessionLocal() as session:
        plans = await _get_plans_list(session)

    if not plans:
        text = "Нет планов. Добавь первый?"
        kb = add_only_keyboard(PLANS_PREFIX, "➕ Добавить план")
    else:
        lines = [_format_plan(p) for p in plans]
        text = "💛 Наши планы:\n\n" + "\n".join(lines)
        kb = list_keyboard(PLANS_PREFIX, [p.id for p in plans], "➕ Добавить план")

    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == f"{PLANS_PREFIX}_add")
async def plan_add_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PlanState.waiting_for_title)
    await callback.message.edit_text("Напиши название события")
    await callback.answer()


@router.message(PlanState.waiting_for_title)
async def plan_create(message: Message, state: FSMContext):
    dt = datetime.utcnow()
    remind = dt - timedelta(minutes=70)

    async with SessionLocal() as session:
        session.add(
            Plan(
                author=message.from_user.id,
                title=message.text,
                dt_start=dt,
                remind_at=remind,
            )
        )
        await session.commit()

    await message.answer("План создан 💛")
    await state.clear()


@router.callback_query(F.data.startswith(f"{PLANS_PREFIX}_edit_"))
async def plan_edit_start(callback: CallbackQuery, state: FSMContext):
    plan_id = int(callback.data.split("_")[-1])
    await state.update_data(plan_id=plan_id)
    await state.set_state(PlanState.waiting_for_edit)
    await callback.message.edit_text("Напиши новое название события")
    await callback.answer()


@router.message(PlanState.waiting_for_edit)
async def plan_edit_save(message: Message, state: FSMContext):
    data = await state.get_data()
    plan_id = data.get("plan_id")
    await state.clear()

    if not plan_id:
        await message.answer("Ошибка: план не найден")
        return

    async with SessionLocal() as session:
        plan = await session.get(Plan, plan_id)
        if not plan:
            await message.answer("План не найден")
            return
        plan.title = message.text
        plan.updated_at = datetime.utcnow()
        await session.commit()

    await message.answer("План обновлён 💛")


@router.callback_query(F.data.startswith(f"{PLANS_PREFIX}_del_"))
async def plan_delete(callback: CallbackQuery):
    plan_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        plan = await session.get(Plan, plan_id)
        if plan:
            await session.delete(plan)
            await session.commit()

    await callback.answer("Удалено")
    await callback.message.edit_text("План удалён 💛")
