from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def pagination_keyboard(action_prefix: str, page: int, total_pages: int):
    """
    ساخت کیبورد صفحه‌بندی

    action_prefix: مثل "products_page" یا "sales_page"
    """
    keyboard = InlineKeyboardMarkup(row_width=2)

    buttons = []

    if page > 1:
        buttons.append(
            InlineKeyboardButton("⬅️ قبلی", callback_data=f"{action_prefix}_{page - 1}")
        )

    if page < total_pages:
        buttons.append(
            InlineKeyboardButton("بعدی ➡️", callback_data=f"{action_prefix}_{page + 1}")
        )

    for btn in buttons:
        keyboard.add(btn)

    return keyboard
