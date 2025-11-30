from telebot import types
from .pagination import pagination_keyboard

def inventory_menu_keyboard():
    """صفحه‌کلید منوی موجودی"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ اضافه کردن محصول", callback_data="add_product"))
    markup.add(types.InlineKeyboardButton("✏️ ویرایش محصولات", callback_data="edit_product_list"))
    markup.add(types.InlineKeyboardButton("📋 مشاهده لیست", callback_data="view_inventory"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup

def edit_product_keyboard(product_id):
    """صفحه‌کلید ویرایش محصول"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ ویرایش نام", callback_data=f"edit_name_{product_id}"))
    markup.add(types.InlineKeyboardButton("📦 ویرایش موجودی", callback_data=f"edit_qty_{product_id}"))
    markup.add(types.InlineKeyboardButton("🗑️ حذف محصول", callback_data=f"delete_product_{product_id}"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_inventory"))
    return markup

def products_list_keyboard_with_pagination(products, page: int, total_pages: int, for_sale=False):
    """صفحه‌کلید لیست محصولات با صفحه‌بندی"""
    markup = types.InlineKeyboardMarkup()
    
    # دکمه‌های محصولات
    for product in products:
        quantity = int(product['quantity'])
        if for_sale:
            if quantity > 0:
                btn_text = f"✅ {product['name']} ({quantity} عدد)"
            else:
                btn_text = f"❌ {product['name']} (ناموجود)"
        else:
            btn_text = f"📦 {product['name']} ({quantity} عدد)"
        
        btn = types.InlineKeyboardButton(
            btn_text,
            callback_data=f"select_product_{product['id']}"
        )
        markup.add(btn)
    
    # دکمه‌های صفحه‌بندی
    pagination_kb = pagination_keyboard("edit_products_page" if not for_sale else "sale_products_page", page, total_pages)
    for row in pagination_kb.keyboard:
        markup.row(*row)
    
    # دکمه بازگشت
    if for_sale:
        back_btn = types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_sales")
    else:
        back_btn = types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_inventory")
    
    markup.add(back_btn)
    
    return markup
