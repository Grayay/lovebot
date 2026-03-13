from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database import SessionLocal
from models.wishlist import WishlistItem
from config import HER_ID

from keyboards.inline import list_keyboard, add_only_keyboard

router = Router()

WISHLIST_PREFIX = "wish"


class WishState(StatesGroup):
    waiting_item = State()
    waiting_edit = State()


async def _get_wishlist(session) -> list[WishlistItem]:
    result = await session.execute(select(WishlistItem).order_by(WishlistItem.id))
    return list(result.scalars().all())


@router.message(F.text == "🛍 Виш-лист")
async def wishlist_list(message: Message):
    async with SessionLocal() as session:
        items = await _get_wishlist(session)

    if not items:
        text = "Виш-лист пуст. Добавь желание?"
        kb = add_only_keyboard(WISHLIST_PREFIX, "➕ Добавить") if message.from_user.id == HER_ID else None
    else:
        lines = [f"• {item.item}" for item in items]
        text = "🛍 Виш-лист:\n\n" + "\n".join(lines)
        if message.from_user.id == HER_ID:
            kb = list_keyboard(WISHLIST_PREFIX, [i.id for i in items], "➕ Добавить")
        else:
            kb = None

    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == f"{WISHLIST_PREFIX}_add")
async def wishlist_add_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != HER_ID:
        await callback.answer("Только она может добавлять в виш-лист 💜")
        return
    await state.set_state(WishState.waiting_item)
    await callback.message.edit_text("Добавь желание")
    await callback.answer()


@router.message(WishState.waiting_item)
async def wishlist_add(message: Message, state: FSMContext):
    if message.from_user.id != HER_ID:
        await state.clear()
        return

    async with SessionLocal() as session:
        session.add(
            WishlistItem(
                owner=message.from_user.id,
                item=message.text,
            )
        )
        await session.commit()

    await message.answer("Желание сохранено 🛍")
    await state.clear()


@router.callback_query(F.data.startswith(f"{WISHLIST_PREFIX}_edit_"))
async def wishlist_edit_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != HER_ID:
        await callback.answer("Только она может редактировать 💜")
        return
    item_id = int(callback.data.split("_")[-1])
    await state.update_data(item_id=item_id)
    await state.set_state(WishState.waiting_edit)
    await callback.message.edit_text("Напиши новый текст желания")
    await callback.answer()


@router.message(WishState.waiting_edit)
async def wishlist_edit_save(message: Message, state: FSMContext):
    if message.from_user.id != HER_ID:
        await state.clear()
        return
    data = await state.get_data()
    item_id = data.get("item_id")
    await state.clear()

    if not item_id:
        await message.answer("Ошибка: элемент не найден")
        return

    async with SessionLocal() as session:
        item = await session.get(WishlistItem, item_id)
        if not item:
            await message.answer("Элемент не найден")
            return
        item.item = message.text
        await session.commit()

    await message.answer("Желание обновлено 🛍")


@router.callback_query(F.data.startswith(f"{WISHLIST_PREFIX}_del_"))
async def wishlist_delete(callback: CallbackQuery):
    if callback.from_user.id != HER_ID:
        await callback.answer("Только она может удалять 💜")
        return
    item_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        item = await session.get(WishlistItem, item_id)
        if item:
            await session.delete(item)
            await session.commit()

    await callback.answer("Удалено")
    await callback.message.edit_text("Желание удалено 🛍")
