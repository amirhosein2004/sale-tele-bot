from telebot import types
from .pagination import pagination_keyboard

def sales_menu_keyboard():
    """صفحه‌کلید منوی فروش"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ ثبت فروش جدید", callback_data="add_sale"))
    markup.add(types.InlineKeyboardButton("📋 مشاهده فروش‌ها", callback_data="view_sales_list"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup

def edit_sale_keyboard(sale_id):
    """صفحه‌کلید ویرایش فروش"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ ویرایش", callback_data=f"edit_sale_{sale_id}"))
    markup.add(types.InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_sale_{sale_id}"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_sales"))
    return markup

def sales_list_keyboard_with_pagination(sales, page: int, total_pages: int):
    """صفحه‌کلید لیست فروش‌ها با صفحه‌بندی"""
    markup = types.InlineKeyboardMarkup()
    
    # دکمه‌های فروش‌ها
    for sale in sales:
        markup.add(types.InlineKeyboardButton(
            f"🔹 {sale['product_name']} - {sale['date']}",
            callback_data=f"select_sale_{sale['id']}"
        ))
    
    # دکمه‌های صفحه‌بندی
    pagination_kb = pagination_keyboard("sales_page", page, total_pages)
    for row in pagination_kb.keyboard:
        markup.row(*row)
    
    # دکمه بازگشت
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_sales"))
    
    return markup
