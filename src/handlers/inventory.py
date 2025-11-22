# هندلرهای مدیریت موجودی محصولات
from ..keyboards import (
    inventory_menu_keyboard,
    products_list_keyboard,
    edit_product_keyboard,
    back_button,
    confirmation_keyboard
)
from .state import (
    get_user_state,
    set_user_state,
    get_user_data,
    is_user_processing,
    set_user_processing
)


def register_inventory_handlers(bot, data_manager):
    """ثبت هندلرهای موجودی محصولات"""
    
    # ============ منوی موجودی ============
    
    @bot.callback_query_handler(func=lambda call: call.data == "inventory_menu")
    def inventory_menu(call):
        """منوی موجودی محصولات"""
        user_id = call.message.chat.id
        set_user_state(user_id, 'inventory_menu')
        
        bot.edit_message_text(
            "📦 منوی موجودی محصولات",
            user_id,
            call.message.message_id,
            reply_markup=inventory_menu_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_inventory")
    def back_to_inventory(call):
        """بازگشت به منوی موجودی"""
        user_id = call.message.chat.id
        set_user_state(user_id, 'inventory_menu')
        
        bot.edit_message_text(
            "📦 منوی موجودی محصولات",
            user_id,
            call.message.message_id,
            reply_markup=inventory_menu_keyboard()
        )
    
    # ============ اضافه کردن محصول ============
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_product")
    def add_product_start(call):
        """شروع فرآیند اضافه کردن محصول"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            set_user_state(user_id, 'add_product_name')
            
            msg = bot.send_message(user_id, "📝 لطفاً نام محصول را وارد کنید:")
            bot.register_next_step_handler(msg, process_product_name, bot)
        finally:
            set_user_processing(user_id, False)
    
    def process_product_name(message, bot):
        """دریافت نام محصول"""
        user_id = message.chat.id
        product_name = message.text.strip()
        
        if not product_name:
            msg = bot.send_message(user_id, "❌ نام محصول نمی‌تواند خالی باشد. دوباره تلاش کنید:")
            bot.register_next_step_handler(msg, process_product_name, bot)
            return
        
        get_user_data(user_id)['product_name'] = product_name
        set_user_state(user_id, 'add_product_qty')
        
        msg = bot.send_message(user_id, "📦 لطفاً موجودی اولیه را وارد کنید (عدد):")
        bot.register_next_step_handler(msg, process_product_quantity, bot)
    
    def process_product_quantity(message, bot):
        """دریافت موجودی محصول"""
        user_id = message.chat.id
        user_data_dict = get_user_data(user_id)
        
        try:
            quantity = int(message.text.strip())
            if quantity < 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_product_quantity, bot)
            return
        
        product_name = user_data_dict.get('product_name')
        if not product_name:
            msg = bot.send_message(user_id, "❌ خطا: نام محصول یافت نشد. لطفاً دوباره تلاش کنید.")
            bot.register_next_step_handler(msg, process_product_name, bot)
            return
        
        data_manager.add_product(product_name, quantity)
        
        bot.send_message(
            user_id,
            f"✅ محصول '{product_name}' با موجودی {quantity} عدد اضافه شد.",
            reply_markup=back_button()
        )
        
        set_user_state(user_id, 'inventory_menu')
    
    # ============ ویرایش محصولات ============
    
    @bot.callback_query_handler(func=lambda call: call.data == "edit_product_list")
    def edit_product_list(call):
        """نمایش لیست محصولات برای ویرایش"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            products = data_manager.get_all_products()
            
            if not products:
                bot.send_message(user_id, "❌ هیچ محصولی برای ویرایش وجود ندارد.", reply_markup=back_button())
                return
            
            set_user_state(user_id, 'edit_product')
            bot.edit_message_text(
                "✏️ محصول مورد نظر را انتخاب کنید:",
                user_id,
                call.message.message_id,
                reply_markup=products_list_keyboard(products)
            )
        finally:
            set_user_processing(user_id, False)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("select_product_") and get_user_state(call.message.chat.id) == 'edit_product')
    def select_product(call):
        """انتخاب محصول برای ویرایش"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            product_id = int(call.data.split("_")[2])
            product = data_manager.get_product(product_id)
            
            if not product:
                bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button())
                return
            
            get_user_data(user_id)['selected_product_id'] = product_id
            
            text = f"📦 محصول: {product['name']}\n"
            text += f"📊 موجودی: {product['quantity']} عدد\n\n"
            text += "چه کاری می‌خواهید انجام دهید؟"
            
            bot.edit_message_text(
                text,
                user_id,
                call.message.message_id,
                reply_markup=edit_product_keyboard(product_id)
            )
        finally:
            set_user_processing(user_id, False)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_name_"))
    def edit_name_start(call):
        """شروع ویرایش نام محصول"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            product_id = int(call.data.split("_")[2])
            product = data_manager.get_product(product_id)
            
            if not product:
                bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button())
                return
            
            get_user_data(user_id)['selected_product_id'] = product_id
            set_user_state(user_id, 'edit_product_name')
            
            msg = bot.send_message(user_id, f"📝 نام جدید را وارد کنید (فعلی: {product['name']}):")
            bot.register_next_step_handler(msg, process_edit_name, bot)
        finally:
            set_user_processing(user_id, False)
    
    def process_edit_name(message, bot):
        """پردازش ویرایش نام محصول"""
        user_id = message.chat.id
        new_name = message.text.strip()
        
        if not new_name:
            msg = bot.send_message(user_id, "❌ نام نمی‌تواند خالی باشد. دوباره تلاش کنید:")
            bot.register_next_step_handler(msg, process_edit_name, bot)
            return
        
        product_id = get_user_data(user_id).get('selected_product_id')
        product = data_manager.get_product(product_id)
        
        data_manager.update_product_name(product_id, new_name)
        
        bot.send_message(
            user_id,
            f"✅ نام محصول از '{product['name']}' به '{new_name}' تغییر یافت.",
            reply_markup=back_button()
        )
        
        set_user_state(user_id, 'inventory_menu')
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_qty_"))
    def edit_quantity_start(call):
        """شروع ویرایش موجودی"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            product_id = int(call.data.split("_")[2])
            product = data_manager.get_product(product_id)
            
            if not product:
                bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button())
                return
            
            get_user_data(user_id)['selected_product_id'] = product_id
            set_user_state(user_id, 'edit_product_qty')
            
            msg = bot.send_message(user_id, f"📝 موجودی جدید را وارد کنید (فعلی: {product['quantity']}):")
            bot.register_next_step_handler(msg, process_edit_quantity, bot)
        finally:
            set_user_processing(user_id, False)
    
    def process_edit_quantity(message, bot):
        """پردازش ویرایش موجودی"""
        user_id = message.chat.id
        
        try:
            new_quantity = int(message.text.strip())
            if new_quantity < 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_edit_quantity, bot)
            return
        
        product_id = get_user_data(user_id).get('selected_product_id')
        product = data_manager.get_product(product_id)
        
        data_manager.update_product_quantity(product_id, new_quantity)
        
        bot.send_message(
            user_id,
            f"✅ موجودی '{product['name']}' به {new_quantity} عدد تغییر یافت.",
            reply_markup=back_button()
        )
        
        set_user_state(user_id, 'inventory_menu')
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_product_"))
    def delete_product(call):
        """حذف محصول با تأیید"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            product_id = int(call.data.split("_")[2])
            product = data_manager.get_product(product_id)
            
            if product:
                bot.edit_message_text(
                    f"⚠️ آیا مطمئن هستید که می‌خواهید محصول '{product['name']}' را حذف کنید؟\n\nاین عمل قابل بازگشت نیست!",
                    user_id,
                    call.message.message_id,
                    reply_markup=confirmation_keyboard("delete_product", product_id)
                )
            else:
                bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button())
        finally:
            set_user_processing(user_id, False)
    
    # ============ مشاهده لیست محصولات ============
    
    @bot.callback_query_handler(func=lambda call: call.data == "view_inventory")
    def view_inventory(call):
        """مشاهده لیست محصولات"""
        user_id = call.message.chat.id
        inventory_text = data_manager.get_products_text()
        
        bot.send_message(
            user_id,
            inventory_text,
            parse_mode="Markdown",
            reply_markup=back_button()
        )
