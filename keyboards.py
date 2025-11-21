# صفحه‌کلیدهای ربات
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


def inventory_menu_keyboard():
    """صفحه‌کلید منوی موجودی"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ اضافه کردن محصول", callback_data="add_product"))
    markup.add(types.InlineKeyboardButton("✏️ ویرایش محصولات", callback_data="edit_product_list"))
    markup.add(types.InlineKeyboardButton("📋 مشاهده لیست", callback_data="view_inventory"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup


def sales_menu_keyboard():
    """صفحه‌کلید منوی فروش"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ ثبت فروش جدید", callback_data="add_sale"))
    markup.add(types.InlineKeyboardButton("📋 مشاهده فروش‌ها", callback_data="view_sales_list"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup


def back_button():
    """دکمه بازگشت"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup


def products_list_keyboard(products, disabled=False, for_sale=False):
    """صفحه‌کلید لیست محصولات"""
    markup = types.InlineKeyboardMarkup()
    for product in products:
        # نمایش وضعیت موجودی
        if for_sale:
            if product['quantity'] > 0:
                status_icon = "✅"
                btn_text = f"{status_icon} {product['name']} ({product['quantity']} عدد)"
            else:
                status_icon = "❌"
                btn_text = f"{status_icon} {product['name']} (ناموجود)"
        else:
            btn_text = f"📦 {product['name']} ({product['quantity']} عدد)"
        
        btn = types.InlineKeyboardButton(
            btn_text,
            callback_data=f"select_product_{product['id']}"
        )
        if disabled or (for_sale and product['quantity'] <= 0):
            btn.callback_data = "disabled"
        markup.add(btn)
    
    back_btn = types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_inventory")
    if disabled:
        back_btn.callback_data = "disabled"
    markup.add(back_btn)
    return markup


def edit_product_keyboard(product_id):
    """صفحه‌کلید ویرایش محصول"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ ویرایش نام", callback_data=f"edit_name_{product_id}"))
    markup.add(types.InlineKeyboardButton("📦 ویرایش موجودی", callback_data=f"edit_qty_{product_id}"))
    markup.add(types.InlineKeyboardButton("🗑️ حذف محصول", callback_data=f"delete_product_{product_id}"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_inventory"))
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


def main_reply_keyboard():
    """صفحه‌کلید کشویی منوی اصلی"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("📦 موجودی محصولات", "💳 ثبت فروش")
    markup.add("📊 گزارش‌ها", "🔧 عملیات سریع")
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


def navigation_keyboard():
    """دکمه‌های ناوبری"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("⬅️ قبلی", callback_data="prev_page"),
        types.InlineKeyboardButton("🏠 خانه", callback_data="back_to_main"),
        types.InlineKeyboardButton("➡️ بعدی", callback_data="next_page")
    )
    return markup


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
    markup.add(types.InlineKeyboardButton("📊 اشتراک گزارش", callback_data="share_report"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup
