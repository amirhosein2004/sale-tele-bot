from telebot import types


def pagination_keyboard(current_page, total_pages, callback_prefix="page"):
    """صفحه‌کلید صفحه‌بندی"""
    markup = types.InlineKeyboardMarkup()
    
    # دکمه‌های ناوبری
    nav_buttons = []
    
    # دکمه قبلی
    if current_page > 1:
        nav_buttons.append(
            types.InlineKeyboardButton("⬅️ قبلی", callback_data=f"{callback_prefix}_prev_{current_page - 1}")
        )
    else:
        nav_buttons.append(
            types.InlineKeyboardButton("⬅️", callback_data="disabled")
        )
    
    # شماره صفحه
    nav_buttons.append(
        types.InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="disabled")
    )
    
    # دکمه بعدی
    if current_page < total_pages:
        nav_buttons.append(
            types.InlineKeyboardButton("بعدی ➡️", callback_data=f"{callback_prefix}_next_{current_page + 1}")
        )
    else:
        nav_buttons.append(
            types.InlineKeyboardButton("➡️", callback_data="disabled")
        )
    
    markup.add(*nav_buttons)
    
    # دکمه بازگشت
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    
    return markup
