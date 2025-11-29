from telebot import types

def inventory_menu_keyboard():
    """صفحه‌کلید منوی موجودی"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ اضافه کردن محصول", callback_data="add_product"))
    markup.add(types.InlineKeyboardButton("✏️ ویرایش محصولات", callback_data="edit_product_list"))
    markup.add(types.InlineKeyboardButton("📋 مشاهده لیست", callback_data="view_inventory"))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main"))
    return markup

def products_list_keyboard(products, disabled=False, for_sale=False):
    """صفحه‌کلید لیست محصولات"""
    markup = types.InlineKeyboardMarkup()
    for product in products:
        # نمایش وضعیت موجودی
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
        if disabled or (for_sale and quantity <= 0):
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
