from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database import SessionLocal
from models.memories import Memory

from keyboards.inline import list_keyboard, add_only_keyboard

router = Router()

MEMORIES_PREFIX = "mem"


class MemoryState(StatesGroup):
    waiting_memory = State()
    waiting_edit = State()


async def _get_memories(session) -> list[Memory]:
    result = await session.execute(select(Memory).order_by(Memory.id))
    return list(result.scalars().all())


@router.message(F.text == "📖 Воспоминания")
async def memories_list(message: Message):
    async with SessionLocal() as session:
        items = await _get_memories(session)

    if not items:
        text = "Нет воспоминаний. Добавь первое?"
        kb = add_only_keyboard(MEMORIES_PREFIX, "➕ Добавить")
    else:
        lines = [f"• {m.text}" for m in items]
        text = "📖 Воспоминания:\n\n" + "\n".join(lines)
        kb = list_keyboard(MEMORIES_PREFIX, [m.id for m in items], "➕ Добавить")

    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == f"{MEMORIES_PREFIX}_add")
async def memory_add_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MemoryState.waiting_memory)
    await callback.message.edit_text("Напиши воспоминание")
    await callback.answer()


@router.message(MemoryState.waiting_memory)
async def memory_create(message: Message, state: FSMContext):
    async with SessionLocal() as session:
        session.add(
            Memory(
                author=message.from_user.id,
                text=message.text,
            )
        )
        await session.commit()

    await message.answer("Воспоминание сохранено 📖")
    await state.clear()


@router.callback_query(F.data.startswith(f"{MEMORIES_PREFIX}_edit_"))
async def memory_edit_start(callback: CallbackQuery, state: FSMContext):
    memory_id = int(callback.data.split("_")[-1])
    await state.update_data(memory_id=memory_id)
    await state.set_state(MemoryState.waiting_edit)
    await callback.message.edit_text("Напиши новый текст воспоминания")
    await callback.answer()


@router.message(MemoryState.waiting_edit)
async def memory_edit_save(message: Message, state: FSMContext):
    data = await state.get_data()
    memory_id = data.get("memory_id")
    await state.clear()

    if not memory_id:
        await message.answer("Ошибка: воспоминание не найдено")
        return

    async with SessionLocal() as session:
        memory = await session.get(Memory, memory_id)
        if not memory:
            await message.answer("Воспоминание не найдено")
            return
        memory.text = message.text
        await session.commit()

    await message.answer("Воспоминание обновлено 📖")


@router.callback_query(F.data.startswith(f"{MEMORIES_PREFIX}_del_"))
async def memory_delete(callback: CallbackQuery):
    memory_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        memory = await session.get(Memory, memory_id)
        if memory:
            await session.delete(memory)
            await session.commit()

    await callback.answer("Удалено")
    await callback.message.edit_text("Воспоминание удалено 📖")
