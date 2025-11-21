# مدیریت پیام‌های ربات
import telebot
from telebot import types
from data_manager import DataManager
from keyboards import *
import threading

data_manager = DataManager()

# ذخیره وضعیت کاربران
user_states = {}
user_data = {}
user_locks = {}  # قفل برای جلوگیری از کلیک‌های چندگانه
processing_users = set()  # کاربرانی که در حال پردازش هستند


def get_user_state(user_id):
    """دریافت وضعیت کاربر"""
    return user_states.get(user_id, 'main_menu')


def set_user_state(user_id, state):
    """تعیین وضعیت کاربر"""
    user_states[user_id] = state


def get_user_data(user_id):
    """دریافت داده‌های موقت کاربر"""
    if user_id not in user_data:
        user_data[user_id] = {}
    return user_data[user_id]


def clear_user_data(user_id):
    """پاک کردن داده‌های موقت کاربر"""
    if user_id in user_data:
        user_data[user_id] = {}


def is_user_processing(user_id):
    """بررسی اینکه آیا کاربر در حال پردازش است"""
    return user_id in processing_users


def set_user_processing(user_id, processing=True):
    """تعیین وضعیت پردازش کاربر"""
    if processing:
        processing_users.add(user_id)
    else:
        processing_users.discard(user_id)


def register_handlers(bot):
    """ثبت تمام هندلرها"""
    
    @bot.message_handler(commands=['start'])
    def start_handler(message):
        """هندلر دستور شروع"""
        user_id = message.chat.id
        set_user_state(user_id, 'main_menu')
        clear_user_data(user_id)
        
        bot.send_message(
            user_id,
            "👋 خوش آمدید!\n\nلطفاً یک گزینه را انتخاب کنید:",
            reply_markup=main_menu_keyboard()
        )
        
        # ارسال صفحه‌کلید کشویی
        bot.send_message(
            user_id,
            "🔽 از منوی زیر نیز می‌توانید استفاده کنید:",
            reply_markup=main_reply_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
    def back_to_main(call):
        """بازگشت به منوی اصلی"""
        user_id = call.message.chat.id
        set_user_state(user_id, 'main_menu')
        clear_user_data(user_id)
        
        bot.edit_message_text(
            "👋 خوش آمدید!\n\nلطفاً یک گزینه را انتخاب کنید:",
            user_id,
            call.message.message_id,
            reply_markup=main_menu_keyboard()
        )
    
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
        
        try:
            quantity = int(message.text.strip())
            if quantity < 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_product_quantity, bot)
            return
        
        user_data_dict = get_user_data(user_id)
        product_name = user_data_dict['product_name']
        
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

    # ============ منوی فروش ============
    
    @bot.callback_query_handler(func=lambda call: call.data == "sales_menu")
    def sales_menu(call):
        """منوی فروش محصولات"""
        user_id = call.message.chat.id
        set_user_state(user_id, 'sales_menu')
        
        bot.edit_message_text(
            "💳 منوی فروش محصولات",
            user_id,
            call.message.message_id,
            reply_markup=sales_menu_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_sales")
    def back_to_sales(call):
        """بازگشت به منوی فروش"""
        user_id = call.message.chat.id
        set_user_state(user_id, 'sales_menu')
        
        bot.edit_message_text(
            "💳 منوی فروش محصولات",
            user_id,
            call.message.message_id,
            reply_markup=sales_menu_keyboard()
        )
    
    # ============ ثبت فروش جدید ============
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_sale")
    def add_sale_start(call):
        """شروع فرآیند ثبت فروش"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            # فقط محصولات با موجودی بیش از صفر را نشان بده
            available_products = data_manager.get_available_products()
            
            if not available_products:
                all_products = data_manager.get_all_products()
                if not all_products:
                    bot.send_message(
                        user_id,
                        "❌ ابتدا باید محصول اضافه کنید.",
                        reply_markup=back_button()
                    )
                else:
                    bot.send_message(
                        user_id,
                        "❌ هیچ محصولی با موجودی کافی برای فروش وجود ندارد.\n\nلطفاً ابتدا موجودی محصولات را تکمیل کنید.",
                        reply_markup=back_button()
                    )
                return
            
            set_user_state(user_id, 'add_sale_product')
            clear_user_data(user_id)
            
            # ایجاد لیست محصولات موجود برای نمایش
            products_text = "📦 *محصولات موجود برای فروش:*\n\n"
            for product in available_products:
                status_icon = "✅" if product['quantity'] > 0 else "❌"
                products_text += f"{status_icon} {product['name']} - موجودی: {product['quantity']} عدد\n"
            
            bot.edit_message_text(
                products_text + "\n\n📝 محصول مورد نظر را از لیست زیر انتخاب کنید:",
                user_id,
                call.message.message_id,
                reply_markup=products_list_keyboard(available_products, for_sale=True),
                parse_mode="Markdown"
            )
        finally:
            set_user_processing(user_id, False)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("select_product_") and get_user_state(call.message.chat.id) == 'add_sale_product')
    def select_product_for_sale(call):
        """انتخاب محصول برای فروش"""
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
            
            # بررسی موجودی
            if product['quantity'] <= 0:
                bot.send_message(
                    user_id, 
                    f"❌ محصول '{product['name']}' موجودی ندارد.\n\nلطفاً محصول دیگری انتخاب کنید یا ابتدا موجودی را تکمیل کنید.",
                    reply_markup=back_button()
                )
                return
            
            get_user_data(user_id)['product_name'] = product['name']
            get_user_data(user_id)['product_id'] = product_id
            get_user_data(user_id)['available_quantity'] = product['quantity']
            set_user_state(user_id, 'add_sale_quantity')
            
            msg = bot.send_message(
                user_id, 
                f"🔢 تعداد فروش را وارد کنید:\n\n📦 موجودی فعلی: {product['quantity']} عدد\n💡 حداکثر قابل فروش: {product['quantity']} عدد"
            )
            bot.register_next_step_handler(msg, process_sale_quantity, bot)
        finally:
            set_user_processing(user_id, False)
    
    def process_sale_quantity(message, bot):
        """دریافت تعداد فروش"""
        user_id = message.chat.id
        
        try:
            quantity = int(message.text.strip())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            user_data_dict = get_user_data(user_id)
            available_qty = user_data_dict.get('available_quantity', 0)
            msg = bot.send_message(
                user_id, 
                f"❌ لطفاً عدد صحیح و مثبت وارد کنید:\n\n📦 موجودی فعلی: {available_qty} عدد"
            )
            bot.register_next_step_handler(msg, process_sale_quantity, bot)
            return
        
        # بررسی موجودی کافی
        user_data_dict = get_user_data(user_id)
        product_id = user_data_dict['product_id']
        available_quantity = user_data_dict['available_quantity']
        
        if quantity > available_quantity:
            msg = bot.send_message(
                user_id, 
                f"❌ موجودی کافی نیست!\n\n📦 موجودی فعلی: {available_quantity} عدد\n🔢 درخواست شما: {quantity} عدد\n\nلطفاً تعداد کمتری وارد کنید:"
            )
            bot.register_next_step_handler(msg, process_sale_quantity, bot)
            return
        
        # بررسی مجدد موجودی در دیتابیس (برای اطمینان)
        if not data_manager.check_inventory(product_id, quantity):
            current_product = data_manager.get_product(product_id)
            current_qty = current_product['quantity'] if current_product else 0
            msg = bot.send_message(
                user_id, 
                f"❌ موجودی تغییر کرده است!\n\n📦 موجودی فعلی: {current_qty} عدد\n\nلطفاً تعداد جدید را وارد کنید:"
            )
            user_data_dict['available_quantity'] = current_qty
            bot.register_next_step_handler(msg, process_sale_quantity, bot)
            return
        
        user_data_dict['quantity'] = quantity
        set_user_state(user_id, 'add_sale_price')
        
        msg = bot.send_message(user_id, "💵 کل مبلغ فروش را وارد کنید:")
        bot.register_next_step_handler(msg, process_sale_price, bot)
    
    def process_sale_price(message, bot):
        """دریافت قیمت فروش"""
        user_id = message.chat.id
        
        try:
            sale_price = float(message.text.strip())
            if sale_price <= 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_sale_price, bot)
            return
        
        get_user_data(user_id)['total_sale_price'] = sale_price
        set_user_state(user_id, 'add_sale_cost')
        
        msg = bot.send_message(user_id, "💸 کل مبلغ خرید (هزینه تهیه) را وارد کنید:")
        bot.register_next_step_handler(msg, process_sale_cost, bot)
    
    def process_sale_cost(message, bot):
        """دریافت هزینه خرید"""
        user_id = message.chat.id
        
        try:
            cost = float(message.text.strip())
            if cost < 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_sale_cost, bot)
            return
        
        get_user_data(user_id)['total_cost'] = cost
        set_user_state(user_id, 'add_sale_extra_cost')
        
        msg = bot.send_message(user_id, "🏷️ هزینه‌های جانبی را وارد کنید (مثل حمل‌ونقل):")
        bot.register_next_step_handler(msg, process_extra_cost, bot)
    
    def process_extra_cost(message, bot):
        """دریافت هزینه‌های جانبی"""
        user_id = message.chat.id
        
        try:
            extra_cost = float(message.text.strip())
            if extra_cost < 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_extra_cost, bot)
            return
        
        get_user_data(user_id)['extra_cost'] = extra_cost
        set_user_state(user_id, 'add_sale_date')
        
        msg = bot.send_message(user_id, "📅 تاریخ فروش را وارد کنید (مثال: 1403/09/29):")
        bot.register_next_step_handler(msg, process_sale_date, bot)
    
    def process_sale_date(message, bot):
        """دریافت تاریخ فروش"""
        user_id = message.chat.id
        sale_date = message.text.strip()
        
        if not sale_date:
            msg = bot.send_message(user_id, "❌ تاریخ نمی‌تواند خالی باشد:")
            bot.register_next_step_handler(msg, process_sale_date, bot)
            return
        
        user_data_dict = get_user_data(user_id)
        
        # بررسی نهایی موجودی قبل از ثبت فروش
        product_id = user_data_dict['product_id']
        quantity = user_data_dict['quantity']
        
        if not data_manager.check_inventory(product_id, quantity):
            current_product = data_manager.get_product(product_id)
            current_qty = current_product['quantity'] if current_product else 0
            bot.send_message(
                user_id,
                f"❌ خطا در ثبت فروش!\n\nموجودی کافی نیست:\n📦 موجودی فعلی: {current_qty} عدد\n🔢 درخواست شما: {quantity} عدد\n\nلطفاً دوباره تلاش کنید.",
                reply_markup=back_button()
            )
            set_user_state(user_id, 'sales_menu')
            return
        
        # محاسبه سود خالص
        total_sale_price = user_data_dict['total_sale_price']
        total_cost = user_data_dict['total_cost']
        extra_cost = user_data_dict['extra_cost']
        net_profit = total_sale_price - total_cost - extra_cost
        
        # ساخت داده‌های فروش
        sale_data = {
            'product_id': product_id,  # اضافه کردن product_id برای مدیریت موجودی
            'product_name': user_data_dict['product_name'],
            'quantity': quantity,
            'sale_price': total_sale_price / quantity,  # قیمت واحد
            'total_sale_price': total_sale_price,
            'total_cost': total_cost,
            'extra_cost': extra_cost,
            'net_profit': net_profit,
            'date': sale_date
        }
        
        # کم کردن موجودی
        if data_manager.reduce_inventory(product_id, quantity):
            # ثبت فروش
            data_manager.add_sale(sale_data)
            
            # نمایش خلاصه
            current_product = data_manager.get_product(product_id)
            remaining_qty = current_product['quantity'] if current_product else 0
            
            summary = format_sale_summary(sale_data)
            summary += f"\n📦 موجودی باقی‌مانده: {remaining_qty} عدد"
            
            bot.send_message(user_id, summary, parse_mode="Markdown", reply_markup=back_button())
        else:
            bot.send_message(
                user_id,
                "❌ خطا در کم کردن موجودی! لطفاً دوباره تلاش کنید.",
                reply_markup=back_button()
            )
        
        set_user_state(user_id, 'sales_menu')
    
    # ============ مشاهده فروش‌ها ============
    
    @bot.callback_query_handler(func=lambda call: call.data == "view_sales_list")
    def view_sales_list(call):
        """مشاهده لیست فروش‌ها"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            sales = data_manager.get_all_sales()
            
            if not sales:
                bot.send_message(user_id, "📊 هیچ فروشی ثبت نشده است.", reply_markup=back_button())
                return
            
            set_user_state(user_id, 'view_sales')
            bot.edit_message_text(
                "📊 لیست فروش‌ها\n\nفروش مورد نظر را انتخاب کنید:",
                user_id,
                call.message.message_id,
                reply_markup=sales_list_keyboard(sales)
            )
        finally:
            set_user_processing(user_id, False)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("select_sale_"))
    def select_sale(call):
        """انتخاب فروش برای ویرایش یا حذف"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            sale_id = int(call.data.split("_")[2])
            sale = data_manager.get_sale(sale_id)
            
            if not sale:
                bot.send_message(user_id, "❌ فروش یافت نشد.", reply_markup=back_button())
                return
            
            get_user_data(user_id)['selected_sale_id'] = sale_id
            
            text = f"�د فروش شماره {sale['id']}\n"
            text += f"📦 محصول: {sale['product_name']}\n"
            text += f"🔢 تعداد: {sale['quantity']}\n"
            text += f"💵 قیمت واحد: {sale['sale_price']}\n"
            text += f"💰 کل فروش: {sale['total_sale_price']}\n"
            text += f"💸 کل خرید: {sale['total_cost']}\n"
            text += f"🏷️ هزینه‌های جانبی: {sale['extra_cost']}\n"
            text += f"📈 سود خالص: {sale['net_profit']}\n"
            text += f"📅 تاریخ: {sale['date']}\n\n"
            text += "چه کاری می‌خواهید انجام دهید؟"
            
            bot.send_message(user_id, text, reply_markup=edit_sale_keyboard(sale_id))
        finally:
            set_user_processing(user_id, False)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_sale_"))
    def delete_sale(call):
        """حذف فروش با تأیید"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            sale_id = int(call.data.split("_")[2])
            sale = data_manager.get_sale(sale_id)
            
            if sale:
                bot.edit_message_text(
                    f"⚠️ آیا مطمئن هستید که می‌خواهید فروش '{sale['product_name']}' را حذف کنید؟\n\nاین عمل قابل بازگشت نیست!",
                    user_id,
                    call.message.message_id,
                    reply_markup=confirmation_keyboard("delete_sale", sale_id)
                )
            else:
                bot.send_message(user_id, "❌ فروش یافت نشد.", reply_markup=back_button())
        finally:
            set_user_processing(user_id, False)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_sale_"))
    def edit_sale_start(call):
        """شروع ویرایش فروش"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            sale_id = int(call.data.split("_")[2])
            sale = data_manager.get_sale(sale_id)
            
            if not sale:
                bot.send_message(user_id, "❌ فروش یافت نشد.", reply_markup=back_button())
                return
            
            get_user_data(user_id)['selected_sale_id'] = sale_id
            get_user_data(user_id)['sale_data'] = sale.copy()
            set_user_state(user_id, 'edit_sale_quantity')
            
            msg = bot.send_message(user_id, f"🔢 تعداد جدید را وارد کنید (فعلی: {sale['quantity']}):")
            bot.register_next_step_handler(msg, process_edit_sale_quantity, bot)
        finally:
            set_user_processing(user_id, False)
    
    def process_edit_sale_quantity(message, bot):
        """پردازش ویرایش تعداد فروش"""
        user_id = message.chat.id
        
        try:
            quantity = int(message.text.strip())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_edit_sale_quantity, bot)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['quantity'] = quantity
        set_user_state(user_id, 'edit_sale_price')
        
        msg = bot.send_message(user_id, f"💵 کل مبلغ فروش جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['total_sale_price']}):")
        bot.register_next_step_handler(msg, process_edit_sale_price, bot)
    
    def process_edit_sale_price(message, bot):
        """پردازش ویرایش قیمت فروش"""
        user_id = message.chat.id
        
        try:
            sale_price = float(message.text.strip())
            if sale_price <= 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_edit_sale_price, bot)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['total_sale_price'] = sale_price
        user_data_dict['sale_data']['sale_price'] = sale_price / user_data_dict['sale_data']['quantity']
        set_user_state(user_id, 'edit_sale_cost')
        
        msg = bot.send_message(user_id, f"💸 کل مبلغ خرید جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['total_cost']}):")
        bot.register_next_step_handler(msg, process_edit_sale_cost, bot)
    
    def process_edit_sale_cost(message, bot):
        """پردازش ویرایش هزینه خرید"""
        user_id = message.chat.id
        
        try:
            cost = float(message.text.strip())
            if cost < 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_edit_sale_cost, bot)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['total_cost'] = cost
        set_user_state(user_id, 'edit_sale_extra_cost')
        
        msg = bot.send_message(user_id, f"🏷️ هزینه‌های جانبی جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['extra_cost']}):")
        bot.register_next_step_handler(msg, process_edit_sale_extra_cost, bot)
    
    def process_edit_sale_extra_cost(message, bot):
        """پردازش ویرایش هزینه‌های جانبی"""
        user_id = message.chat.id
        
        try:
            extra_cost = float(message.text.strip())
            if extra_cost < 0:
                raise ValueError
        except ValueError:
            msg = bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            bot.register_next_step_handler(msg, process_edit_sale_extra_cost, bot)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['extra_cost'] = extra_cost
        set_user_state(user_id, 'edit_sale_date')
        
        msg = bot.send_message(user_id, f"📅 تاریخ جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['date']}):")
        bot.register_next_step_handler(msg, process_edit_sale_date, bot)
    
    def process_edit_sale_date(message, bot):
        """پردازش ویرایش تاریخ فروش"""
        user_id = message.chat.id
        sale_date = message.text.strip()
        
        if not sale_date:
            msg = bot.send_message(user_id, "❌ تاریخ نمی‌تواند خالی باشد:")
            bot.register_next_step_handler(msg, process_edit_sale_date, bot)
            return
        
        user_data_dict = get_user_data(user_id)
        sale_data = user_data_dict['sale_data']
        sale_data['date'] = sale_date
        
        # محاسبه سود خالص
        sale_data['net_profit'] = sale_data['total_sale_price'] - sale_data['total_cost'] - sale_data['extra_cost']
        
        # به‌روزرسانی فروش
        sale_id = user_data_dict['selected_sale_id']
        data_manager.update_sale(sale_id, sale_data)
        
        bot.send_message(user_id, "✅ فروش به‌روزرسانی شد.", reply_markup=back_button())
        set_user_state(user_id, 'view_sales')
    
    # ============ هندلر پیام‌های متنی ============
    
    @bot.message_handler(func=lambda message: True)
    def handle_text_messages(message):
        """هندلر پیام‌های متنی"""
        user_id = message.chat.id
        text = message.text.strip()
        
        # اگر کاربر در حال پردازش است، نادیده بگیر
        if is_user_processing(user_id):
            return
        
        # بررسی پیام‌های صفحه‌کلید کشویی
        if text == "📦 موجودی محصولات":
            set_user_state(user_id, 'inventory_menu')
            bot.send_message(
                user_id,
                "📦 منوی موجودی محصولات",
                reply_markup=inventory_menu_keyboard()
            )
        elif text == "💳 ثبت فروش":
            set_user_state(user_id, 'sales_menu')
            bot.send_message(
                user_id,
                "💳 منوی فروش محصولات",
                reply_markup=sales_menu_keyboard()
            )
        elif text == "📊 گزارش‌ها":
            # نمایش گزارش کلی
            inventory_text = data_manager.get_products_text()
            sales_summary = data_manager.get_sales_summary()
            
            report_text = f"📊 *گزارش کلی*\n\n{inventory_text}\n\n{sales_summary}"
            bot.send_message(
                user_id,
                report_text,
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard()
            )
        elif text == "🔧 عملیات سریع":
            bot.send_message(
                user_id,
                "🔧 عملیات سریع\n\nانتخاب کنید:",
                reply_markup=quick_actions_keyboard()
            )
        elif text == "📖 راهنما":
            help_text = """
📖 *راهنمای استفاده از ربات*

🔹 *مدیریت محصولات:*
• اضافه کردن محصول جدید
• ویرایش نام و موجودی
• حذف محصولات
• مشاهده لیست کامل

🔹 *مدیریت فروش:*
• ثبت فروش جدید
• ویرایش اطلاعات فروش
• حذف فروش‌ها
• مشاهده گزارش‌ها

🔹 *گزارش‌گیری:*
• مشاهده موجودی فعلی
• خلاصه فروش‌ها
• محاسبه سود و زیان

💡 *نکات مهم:*
• همیشه اطلاعات دقیق وارد کنید
• برای لغو عملیات از دکمه بازگشت استفاده کنید
• گزارش‌ها به صورت لحظه‌ای به‌روزرسانی می‌شوند
            """
            bot.send_message(
                user_id,
                help_text,
                parse_mode="Markdown",
                reply_markup=help_keyboard()
            )
        elif text == "📤 اشتراک‌گذاری":
            bot.send_message(
                user_id,
                "📤 اشتراک‌گذاری\n\nگزینه مورد نظر را انتخاب کنید:",
                reply_markup=share_keyboard()
            )
        else:
            # برای هر پیام دیگر، منو را نشان بده
            set_user_state(user_id, 'main_menu')
            clear_user_data(user_id)
            
            bot.send_message(
                user_id,
                "👋 خوش آمدید!\n\nلطفاً یک گزینه را انتخاب کنید:",
                reply_markup=main_menu_keyboard()
            )
    
    # ============ هندلرهای دکمه‌های Inline جدید ============
    
    @bot.callback_query_handler(func=lambda call: call.data == "show_help")
    def show_help(call):
        """نمایش راهنما"""
        user_id = call.message.chat.id
        
        help_text = """
📖 *راهنمای استفاده از ربات*

🔹 *مدیریت محصولات:*
• اضافه کردن محصول جدید
• ویرایش نام و موجودی
• حذف محصولات
• مشاهده لیست کامل

🔹 *مدیریت فروش:*
• ثبت فروش جدید
• ویرایش اطلاعات فروش
• حذف فروش‌ها
• مشاهده گزارش‌ها

🔹 *گزارش‌گیری:*
• مشاهده موجودی فعلی
• خلاصه فروش‌ها
• محاسبه سود و زیان

💡 *نکات مهم:*
• همیشه اطلاعات دقیق وارد کنید
• برای لغو عملیات از دکمه بازگشت استفاده کنید
• گزارش‌ها به صورت لحظه‌ای به‌روزرسانی می‌شوند
        """
        
        bot.edit_message_text(
            help_text,
            user_id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=back_button()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "share_report")
    def share_report(call):
        """اشتراک‌گذاری گزارش"""
        user_id = call.message.chat.id
        
        # تولید گزارش کامل
        inventory_text = data_manager.get_products_text()
        sales_summary = data_manager.get_sales_summary()
        
        report_text = f"📊 *گزارش کامل فروشگاه*\n\n{inventory_text}\n\n{sales_summary}"
        
        bot.send_message(
            user_id,
            report_text,
            parse_mode="Markdown"
        )
        
        bot.answer_callback_query(call.id, "✅ گزارش ارسال شد!")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
    def handle_confirmation(call):
        """مدیریت تأییدیه‌ها"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            parts = call.data.split("_")
            action = parts[1]
            item_id = int(parts[2])
            
            if action == "delete_product":
                product = data_manager.get_product(item_id)
                if product:
                    data_manager.delete_product(item_id)
                    bot.edit_message_text(
                        f"✅ محصول '{product['name']}' حذف شد.",
                        user_id,
                        call.message.message_id,
                        reply_markup=back_button()
                    )
                else:
                    bot.edit_message_text(
                        "❌ محصول یافت نشد.",
                        user_id,
                        call.message.message_id,
                        reply_markup=back_button()
                    )
            
            elif action == "delete_sale":
                sale = data_manager.get_sale(item_id)
                if sale:
                    # بازگرداندن موجودی
                    if 'product_id' in sale:
                        product = data_manager.find_product_by_name(sale['product_name'])
                        if product:
                            data_manager.increase_inventory(product['id'], sale['quantity'])
                    
                    # حذف فروش
                    data_manager.delete_sale(item_id)
                    bot.edit_message_text(
                        f"✅ فروش حذف شد.\n\n📦 موجودی '{sale['product_name']}' بازگردانده شد: +{sale['quantity']} عدد",
                        user_id,
                        call.message.message_id,
                        reply_markup=back_button()
                    )
                else:
                    bot.edit_message_text(
                        "❌ فروش یافت نشد.",
                        user_id,
                        call.message.message_id,
                        reply_markup=back_button()
                    )
            
            set_user_state(user_id, 'main_menu')
        finally:
            set_user_processing(user_id, False)
    
    @bot.callback_query_handler(func=lambda call: call.data == "cancel_action")
    def cancel_action(call):
        """لغو عملیات"""
        user_id = call.message.chat.id
        set_user_state(user_id, 'main_menu')
        
        bot.edit_message_text(
            "❌ عملیات لغو شد.\n\nلطفاً یک گزینه را انتخاب کنید:",
            user_id,
            call.message.message_id,
            reply_markup=main_menu_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data in ["prev_page", "next_page"])
    def handle_pagination(call):
        """مدیریت صفحه‌بندی"""
        user_id = call.message.chat.id
        
        # در حال حاضر فقط پیام اطلاع‌رسانی
        if call.data == "prev_page":
            bot.answer_callback_query(call.id, "📄 صفحه قبلی در دسترس نیست", show_alert=False)
        else:
            bot.answer_callback_query(call.id, "📄 صفحه بعدی در دسترس نیست", show_alert=False)
    
    @bot.callback_query_handler(func=lambda call: call.data == "quick_actions")
    def quick_actions_menu(call):
        """منوی عملیات سریع"""
        user_id = call.message.chat.id
        
        bot.edit_message_text(
            "🔧 عملیات سریع\n\nانتخاب کنید:",
            user_id,
            call.message.message_id,
            reply_markup=quick_actions_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "share_menu")
    def share_menu(call):
        """منوی اشتراک‌گذاری"""
        user_id = call.message.chat.id
        
        bot.edit_message_text(
            "📤 اشتراک‌گذاری\n\nگزینه مورد نظر را انتخاب کنید:",
            user_id,
            call.message.message_id,
            reply_markup=share_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "disabled")
    def disabled_button(call):
        """مدیریت دکمه‌های غیرفعال"""
        bot.answer_callback_query(
            call.id, 
            "❌ این گزینه در حال حاضر در دسترس نیست.", 
            show_alert=True
        )


def format_sale_summary(sale_data):
    """فرمت‌بندی خلاصه فروش"""
    return (
        "✅ *فروش ثبت شد*\n\n"
        f"📦 محصول: {sale_data['product_name']}\n"
        f"🔢 تعداد: {sale_data['quantity']}\n"
        f"💵 قیمت واحد: {sale_data['sale_price']}\n"
        f"💰 کل فروش: {sale_data['total_sale_price']}\n"
        f"💸 کل خرید: {sale_data['total_cost']}\n"
        f"🏷️ هزینه‌های جانبی: {sale_data['extra_cost']}\n"
        f"📈 سود خالص: {sale_data['net_profit']}\n"
        f"📅 تاریخ: {sale_data['date']}\n"
    )
