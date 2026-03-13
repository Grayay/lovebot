from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database import SessionLocal
from models.shopping import HomeProduct

from keyboards.inline import (
    shopping_products_keyboard,
    shopping_list_actions_keyboard,
    shopping_purchase_type_keyboard,
)

router = Router()

SHOP_PREFIX = "shop"


class NewProductState(StatesGroup):
    waiting_name = State()


def _format_category(cat: str) -> str:
    """Display category: delivery/store (map buy_myself for backward compat)."""
    return "store" if cat in ("store", "buy_myself") else "delivery"


def _format_list(products: list[HomeProduct]) -> str:
    if not products:
        return "🛒 Нужно купить:\n\n(пусто)"
    lines = [f"• {p.name} — {_format_category(p.category)}" for p in products]
    return "🛒 Нужно купить:\n\n" + "\n".join(lines)


async def _get_available_products(session) -> list[HomeProduct]:
    """Products in stock (can be added to list)."""
    result = await session.execute(
        select(HomeProduct).where(HomeProduct.is_available == True).order_by(HomeProduct.name)
    )
    return list(result.scalars().all())


async def _get_shopping_list(session) -> list[HomeProduct]:
    """Products in shopping list (need to buy)."""
    result = await session.execute(
        select(HomeProduct).where(HomeProduct.is_available == False).order_by(HomeProduct.name)
    )
    return list(result.scalars().all())


@router.message(F.text == "🛒 Список покупок")
async def shopping_start(message: Message):
    """Show 'What ran out?' with product buttons."""
    async with SessionLocal() as session:
        products = await _get_available_products(session)
        in_list = await _get_shopping_list(session)

    if not products:
        text = _format_list(in_list)
        kb = shopping_list_actions_keyboard()
        await message.answer(text, reply_markup=kb)
        return

    kb = shopping_products_keyboard(products, show_list_btn=len(in_list) > 0)
    await message.answer("🏠 Что закончилось?", reply_markup=kb)


@router.callback_query(F.data.startswith(f"{SHOP_PREFIX}_add_"))
async def shopping_add_product(callback: CallbackQuery):
    """Add product to list (set is_available=False)."""
    product_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        product = await session.get(HomeProduct, product_id)
        if product:
            product.is_available = False
            await session.commit()

    async with SessionLocal() as session:
        in_list = await _get_shopping_list(session)
        available = await _get_available_products(session)

    text = _format_list(in_list)

    kb = shopping_list_actions_keyboard()
    if available:
        kb.inline_keyboard.insert(0, [InlineKeyboardButton(text="🏠 Что закончилось?", callback_data=f"{SHOP_PREFIX}_what")])

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer(f"Добавлено: {product.name}" if product else "Готово")


@router.callback_query(F.data == f"{SHOP_PREFIX}_show")
async def shopping_show_list(callback: CallbackQuery):
    """Show current shopping list with action buttons."""
    async with SessionLocal() as session:
        in_list = await _get_shopping_list(session)
        available = await _get_available_products(session)

    text = _format_list(in_list)
    kb = shopping_list_actions_keyboard()

    if available:
        kb.inline_keyboard.insert(0, [InlineKeyboardButton(text="🏠 Что закончилось?", callback_data=f"{SHOP_PREFIX}_what")])

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == f"{SHOP_PREFIX}_what")
async def shopping_what_ran_out(callback: CallbackQuery):
    """Show product selection again."""
    async with SessionLocal() as session:
        products = await _get_available_products(session)

    if not products:
        await callback.answer("Все продукты уже в списке")
        return

    await callback.message.edit_text("🏠 Что закончилось?", reply_markup=shopping_products_keyboard(products))
    await callback.answer()


@router.callback_query(F.data == f"{SHOP_PREFIX}_clear")
async def shopping_clear_all(callback: CallbackQuery):
    """Set all products to available (clear list)."""
    async with SessionLocal() as session:
        result = await session.execute(select(HomeProduct).where(HomeProduct.is_available == False))
        products = result.scalars().all()
        for p in products:
            p.is_available = True
        await session.commit()

    async with SessionLocal() as session:
        available = await _get_available_products(session)

    if available:
        await callback.message.edit_text(
            "Список очищен 👍\n\n🏠 Что закончилось?",
            reply_markup=shopping_products_keyboard(available),
        )
    else:
        await callback.message.edit_text("Список очищен 👍\n\nВсе продукты есть дома.")
    await callback.answer("Список очищен")


@router.callback_query(F.data == f"{SHOP_PREFIX}_new")
async def shopping_new_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NewProductState.waiting_name)
    await callback.message.edit_text("Введите название продукта")
    await callback.answer()


@router.message(NewProductState.waiting_name)
async def shopping_new_name_received(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Введите название")
        return

    await state.update_data(product_name=name)
    await message.answer("Как купить?", reply_markup=shopping_purchase_type_keyboard())


@router.callback_query(F.data.in_([f"{SHOP_PREFIX}_type_delivery", f"{SHOP_PREFIX}_type_store"]))
async def shopping_new_type_selected(callback: CallbackQuery, state: FSMContext):
    if not await state.get_state():
        await callback.answer("Сессия истекла. Начните заново.")
        return

    data = await state.get_data()
    name = data.get("product_name")
    await state.clear()

    if not name:
        await callback.message.edit_text("Ошибка. Начните заново.")
        await callback.answer()
        return

    category = "delivery" if callback.data == f"{SHOP_PREFIX}_type_delivery" else "store"

    async with SessionLocal() as session:
        session.add(HomeProduct(name=name, category=category))
        await session.commit()

    await callback.message.edit_text(f"Продукт «{name}» добавлен в список 🛒")
    await callback.answer()
