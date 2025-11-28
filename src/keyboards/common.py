from telebot import types

def main_menu_keyboard():
    """صفحه‌کلید منوی اصلی"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📦 موجودی محصولات", callback_data="inventory_menu"))
    markup.add(types.InlineKeyboardButton("💳 ثبت فروش", callback_data="sales_menu"))
    markup.add(
        types.InlineKeyboardButton("🔧 عملیات سریع", callback_data="quick_actions"),
        types.InlineKeyboardButton("📖 راهنما", callback_data="show_help")
    )
    markup.add(types.InlineKeyboardButton("📤 اشتراک‌گذاری", callback_data="share_menu"))
    return markup


def back_button():
    """دکمه بازگشت"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup


def main_reply_keyboard():
    """صفحه‌کلید کشویی منوی اصلی"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("📦 موجودی محصولات", "💳 ثبت فروش")
    markup.add("📊 گزارش خلاصه", "🔧 عملیات سریع")
    markup.add("📖 راهنما", "📤 اشتراک‌گذاری")
    return markup


def remove_keyboard():
    """حذف صفحه‌کلید کشویی"""
    return types.ReplyKeyboardRemove()


def quick_actions_keyboard():
    """دکمه‌های عملیات سریع (Inline)"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ محصول جدید", callback_data="add_product"),
        types.InlineKeyboardButton("💳 فروش جدید", callback_data="add_sale")
    )
    markup.add(
        types.InlineKeyboardButton("📋 مشاهده موجودی", callback_data="view_inventory"),
        types.InlineKeyboardButton("📊 مشاهده فروش‌ها", callback_data="view_sales_list")
    )
    markup.add(types.InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_to_main"))
    return markup


def confirmation_keyboard(action, item_id):
    """دکمه‌های تأیید و لغو"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تأیید", callback_data=f"confirm_{action}_{item_id}"),
        types.InlineKeyboardButton("❌ لغو", callback_data="cancel_action")
    )
    return markup


# def navigation_keyboard():
#     """دکمه‌های ناوبری"""
#     markup = types.InlineKeyboardMarkup()
#     markup.add(
#         types.InlineKeyboardButton("⬅️ قبلی", callback_data="prev_page"),
#         types.InlineKeyboardButton("🏠 خانه", callback_data="back_to_main"),
#         types.InlineKeyboardButton("➡️ بعدی", callback_data="next_page")
#     )
#     return markup


def help_keyboard():
    """دکمه‌های راهنما"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📖 راهنمای استفاده", callback_data="show_help"))
    markup.add(types.InlineKeyboardButton("📞 پشتیبانی", url="https://t.me/your_support"))
    markup.add(types.InlineKeyboardButton("🌐 وب‌سایت", url="https://your-website.com"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup


def share_keyboard():
    """دکمه‌های اشتراک‌گذاری"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📤 اشتراک‌گذاری ربات", switch_inline_query="استفاده از ربات مدیریت فروش"))
    markup.add(types.InlineKeyboardButton("📊 اشتراک گزارش کامل", callback_data="share_full_report"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup
