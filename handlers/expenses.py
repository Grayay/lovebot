from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import SessionLocal
from models.expenses import Expense

from keyboards.inline import expense_type_keyboard

router = Router()


class ExpenseState(StatesGroup):
    waiting_amount = State()


@router.message(F.text == "💰 Потраченные деньги")
async def expense_start(message: Message, state: FSMContext):
    await state.set_state(ExpenseState.waiting_amount)
    await message.answer("Введите сумму")


@router.message(ExpenseState.waiting_amount)
async def expense_amount_received(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Введите число")
        return

    if amount <= 0:
        await message.answer("Сумма должна быть больше нуля")
        return

    await state.update_data(amount=amount)
    await message.answer("На себя или на нас?", reply_markup=expense_type_keyboard())


@router.callback_query(F.data.in_(["expense_self", "expense_couple"]))
async def expense_type_selected(callback: CallbackQuery, state: FSMContext):
    if not await state.get_state():
        await callback.answer("Сессия истекла. Введите сумму заново.")
        return

    data = await state.get_data()
    amount = data.get("amount")
    await state.clear()

    if not amount:
        await callback.message.edit_text("Ошибка. Начните заново: нажмите 💰 Потраченные деньги")
        await callback.answer()
        return

    expense_type = "self" if callback.data == "expense_self" else "couple"

    async with SessionLocal() as session:
        session.add(
            Expense(
                author_id=callback.from_user.id,
                amount=amount,
                type=expense_type,
            )
        )
        await session.commit()

    type_label = "на себя" if expense_type == "self" else "на нас"
    await callback.message.edit_text(f"Трата {amount} ₽ ({type_label}) сохранена 💰")
    await callback.answer()
