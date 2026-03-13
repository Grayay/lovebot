from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🩺 Самочувствие"), KeyboardButton(text="🥰 Соскучилась")],
        [KeyboardButton(text="🎯 Наши цели"), KeyboardButton(text="💛 Наши планы")],
        [KeyboardButton(text="🛒 Список покупок"), KeyboardButton(text="💬 Нужно обсудить")],
        [KeyboardButton(text="🎁 Получить подарок"), KeyboardButton(text="✨ Идеи свиданий")],
        [KeyboardButton(text="📖 Воспоминания"), KeyboardButton(text="💰 Потраченные деньги")],
        [KeyboardButton(text="🛍 Виш-лист")]
    ],
    resize_keyboard=True
)