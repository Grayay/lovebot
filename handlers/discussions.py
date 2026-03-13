from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database import SessionLocal
from models.discussions import DiscussionTopic

from keyboards.inline import list_keyboard, add_only_keyboard

router = Router()

TOPICS_PREFIX = "disc"


class TopicState(StatesGroup):
    waiting_topic = State()
    waiting_edit = State()


async def _get_topics(session) -> list[DiscussionTopic]:
    result = await session.execute(select(DiscussionTopic).order_by(DiscussionTopic.id))
    return list(result.scalars().all())


@router.message(F.text == "💬 Нужно обсудить")
async def topics_list(message: Message):
    async with SessionLocal() as session:
        topics = await _get_topics(session)

    if not topics:
        text = "Нет тем для обсуждения. Добавь первую?"
        kb = add_only_keyboard(TOPICS_PREFIX, "➕ Добавить тему")
    else:
        lines = [f"• {t.text}" for t in topics]
        text = "💬 Нужно обсудить:\n\n" + "\n".join(lines)
        kb = list_keyboard(TOPICS_PREFIX, [t.id for t in topics], "➕ Добавить тему")

    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == f"{TOPICS_PREFIX}_add")
async def topic_add_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TopicState.waiting_topic)
    await callback.message.edit_text("Напиши тему")
    await callback.answer()


@router.message(TopicState.waiting_topic)
async def topic_create(message: Message, state: FSMContext):
    async with SessionLocal() as session:
        session.add(
            DiscussionTopic(
                author=message.from_user.id,
                text=message.text,
            )
        )
        await session.commit()

    await message.answer("Тема сохранена 💬")
    await state.clear()


@router.callback_query(F.data.startswith(f"{TOPICS_PREFIX}_edit_"))
async def topic_edit_start(callback: CallbackQuery, state: FSMContext):
    topic_id = int(callback.data.split("_")[-1])
    await state.update_data(topic_id=topic_id)
    await state.set_state(TopicState.waiting_edit)
    await callback.message.edit_text("Напиши новый текст темы")
    await callback.answer()


@router.message(TopicState.waiting_edit)
async def topic_edit_save(message: Message, state: FSMContext):
    data = await state.get_data()
    topic_id = data.get("topic_id")
    await state.clear()

    if not topic_id:
        await message.answer("Ошибка: тема не найдена")
        return

    async with SessionLocal() as session:
        topic = await session.get(DiscussionTopic, topic_id)
        if not topic:
            await message.answer("Тема не найдена")
            return
        topic.text = message.text
        await session.commit()

    await message.answer("Тема обновлена 💬")


@router.callback_query(F.data.startswith(f"{TOPICS_PREFIX}_del_"))
async def topic_delete(callback: CallbackQuery):
    topic_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        topic = await session.get(DiscussionTopic, topic_id)
        if topic:
            await session.delete(topic)
            await session.commit()

    await callback.answer("Удалено")
    await callback.message.edit_text("Тема удалена 💬")
