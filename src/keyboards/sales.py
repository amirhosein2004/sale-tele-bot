from telebot import types

def sales_menu_keyboard():
    """صفحه‌کلید منوی فروش"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ ثبت فروش جدید", callback_data="add_sale"))
    markup.add(types.InlineKeyboardButton("📋 مشاهده فروش‌ها", callback_data="view_sales_list"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup

def sales_list_keyboard(sales):
    """صفحه‌کلید لیست فروش‌ها"""
    markup = types.InlineKeyboardMarkup()
    for sale in sales:
        markup.add(types.InlineKeyboardButton(
            f"🔹 {sale['product_name']} - {sale['date']}",
            callback_data=f"select_sale_{sale['id']}"
        ))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup

def edit_sale_keyboard(sale_id):
    """صفحه‌کلید ویرایش فروش"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ ویرایش", callback_data=f"edit_sale_{sale_id}"))
    markup.add(types.InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_sale_{sale_id}"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_sales"))
    return markup
