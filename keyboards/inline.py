from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def mood_keyboard():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data="mood_1"),
                InlineKeyboardButton(text="2", callback_data="mood_2"),
                InlineKeyboardButton(text="3", callback_data="mood_3"),
                InlineKeyboardButton(text="4", callback_data="mood_4"),
                InlineKeyboardButton(text="5", callback_data="mood_5"),
            ],
            [
                InlineKeyboardButton(text="6", callback_data="mood_6"),
                InlineKeyboardButton(text="7", callback_data="mood_7"),
                InlineKeyboardButton(text="8", callback_data="mood_8"),
                InlineKeyboardButton(text="9", callback_data="mood_9"),
                InlineKeyboardButton(text="10", callback_data="mood_10"),
            ],
        ]
    )

    return keyboard


def miss_keyboard():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤗 Обнимашки", callback_data="miss_hug")],
            [InlineKeyboardButton(text="😘 Поцелуйчик", callback_data="miss_kiss")],
            [InlineKeyboardButton(text="🔥 Страстный поцелуй", callback_data="miss_hotkiss")],
            [InlineKeyboardButton(text="💆 Хрустнуть спинку", callback_data="miss_back")],
        ]
    )

    return keyboard


def item_actions_keyboard(prefix: str, item_id: int) -> InlineKeyboardMarkup:
    """Inline keyboard with Edit and Delete for a list item."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Изменить", callback_data=f"{prefix}_edit_{item_id}"),
                InlineKeyboardButton(text="🗑 Удалить", callback_data=f"{prefix}_del_{item_id}"),
            ]
        ]
    )


def list_keyboard(prefix: str, item_ids: list[int], add_label: str = "➕ Добавить") -> InlineKeyboardMarkup:
    """Inline keyboard with item rows (Edit, Delete) and Add button."""
    rows = []
    for item_id in item_ids:
        rows.append([
            InlineKeyboardButton(text="✏️ Изменить", callback_data=f"{prefix}_edit_{item_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"{prefix}_del_{item_id}"),
        ])
    rows.append([InlineKeyboardButton(text=add_label, callback_data=f"{prefix}_add")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def add_only_keyboard(prefix: str, label: str = "➕ Добавить") -> InlineKeyboardMarkup:
    """Inline keyboard with only Add button (for empty list)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=f"{prefix}_add")]]
    )


def dates_list_keyboard(prefix: str, item_ids: list[int], add_label: str = "➕ Добавить идею") -> InlineKeyboardMarkup:
    """Inline keyboard for dates: item rows (Edit, Delete), Add, and Random date idea button."""
    rows = []
    for item_id in item_ids:
        rows.append([
            InlineKeyboardButton(text="✏️ Изменить", callback_data=f"{prefix}_edit_{item_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"{prefix}_del_{item_id}"),
        ])
    rows.append([InlineKeyboardButton(text=add_label, callback_data=f"{prefix}_add")])
    rows.append([InlineKeyboardButton(text="🎲 Random date idea", callback_data=f"{prefix}_random")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def expense_type_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for expense type: self or couple."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 На себя", callback_data="expense_self"),
                InlineKeyboardButton(text="❤️ На нас", callback_data="expense_couple"),
            ]
        ]
    )


def shopping_products_keyboard(products: list, show_list_btn: bool = False) -> InlineKeyboardMarkup:
    """Inline keyboard with product buttons (2 per row)."""
    rows = []
    row = []
    for p in products:
        row.append(InlineKeyboardButton(text=p.name, callback_data=f"shop_add_{p.id}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    if show_list_btn:
        rows.append([InlineKeyboardButton(text="📋 Показать список", callback_data="shop_show")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shopping_list_actions_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard: Add new product, Clear all."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Новый продукт", callback_data="shop_new")],
            [InlineKeyboardButton(text="🧹 Всё купили", callback_data="shop_clear")],
        ]
    )


def shopping_purchase_type_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for new product purchase type."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚚 Доставка", callback_data="shop_type_delivery"),
                InlineKeyboardButton(text="🏪 Магазин", callback_data="shop_type_store"),
            ]
        ]
    )


def dates_add_only_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Inline keyboard for empty dates list: Add and Random buttons."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить идею", callback_data=f"{prefix}_add")],
            [InlineKeyboardButton(text="🎲 Random date idea", callback_data=f"{prefix}_random")],
        ]
    )