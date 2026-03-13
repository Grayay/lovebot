from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.inline import miss_keyboard
from config import ADMIN_ID

router = Router()


@router.message(F.text == "🥰 Соскучилась")
async def miss_start(message: Message):
    await message.answer("Что именно хочется?", reply_markup=miss_keyboard())


@router.callback_query(F.data.startswith("miss_"))
async def miss_selected(callback: CallbackQuery):
    action = callback.data.split("_")[1]

    actions = {
        "hug": "обнимашки",
        "kiss": "поцелуйчик",
        "hotkiss": "страстный поцелуй",
        "back": "хрустнуть спинку",
    }

    await callback.message.edit_text("Сообщение отправлено 💜")

    await callback.bot.send_message(
        ADMIN_ID,
        f"💌 Она соскучилась\n\nХочет: {actions.get(action)}"
    )

    await callback.answer()