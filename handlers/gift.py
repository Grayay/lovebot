from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import HER_ID

router = Router()

quest_step = {}


def found_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="❤️ Нашла", callback_data="gift_found")
    return kb.as_markup()


@router.message(F.text == "🎁 Получить подарок")
async def start_gift(message: Message):

    if message.from_user.id != HER_ID:
        return

    quest_step[message.from_user.id] = 1

    await message.answer(
"""Я официальный помощник Сергея по презентации подарков на идеальное 8 марта 🌸

Сегодня тебя ждёт небольшой квест.

Правило одно:
ничего не спрятано.
Все предметы находятся на самом видном месте — примерно на уровне глаз.

Первое задание.

Найди предмет, который делает твои губы ещё красивее
и ещё слаще.

Он находится там, где мы часто пьём вкусный какао
и смотрим уютные сериалы.""",
        reply_markup=found_keyboard()
    )


@router.callback_query(F.data == "gift_found")
async def next_step(callback: CallbackQuery):

    user_id = callback.from_user.id

    if user_id not in quest_step:
        return

    step = quest_step[user_id]

    if step == 1:
        quest_step[user_id] = 2

        await callback.message.answer(
"""Отлично ❤️

Но одних сладких губ для праздника мало.

Теперь найди то, что делает день ещё немного слаще.

То, что обычно появляется,
когда хочется порадовать себя
или отметить что-то хорошее."""
        )

    elif step == 2:
        quest_step[user_id] = 3

        await callback.message.answer(
"""Если тебе понравился предыдущий подарок,
думаю, этот тоже вызовет улыбку.

Отправляйся туда,
где есть зеркало,
в которое можно посмотреть
на эти красивые губы
и на счастливую девушку."""
        )

    elif step == 3:
        quest_step[user_id] = 4

        await callback.message.answer(
"""Ты отлично справляешься.

Следующий подарок находится в комнате.

Это что-то очень простое,
но способное сделать любой день
немного красивее
и немного теплее."""
        )

    elif step == 4:
        quest_step[user_id] = 5

        await callback.message.answer(
"""И последнее.

Этот подарок не самый практичный в мире,
но он очень милый.

Он состоит из двух фигур,
выполнен в твоём любимом цвете
и просто создан для того,
чтобы иногда на него смотреть
и улыбаться.

Он тоже ждёт тебя в комнате."""
        )

    elif step == 5:

        quest_step.pop(user_id)

        await callback.message.answer(
"""С 8 марта ❤️

Ты невероятная девушка,
и я очень рад,
что именно ты рядом со мной."""
        )

    await callback.answer()