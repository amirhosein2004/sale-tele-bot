# هندلرهای مدیریت فروش
from ..keyboards import (
    sales_menu_keyboard,
    sales_list_keyboard,
    edit_sale_keyboard,
    back_button,
    confirmation_keyboard,
    products_list_keyboard
)
from .state import (
    get_user_state,
    set_user_state,
    get_user_data,
    clear_user_data,
    is_user_processing,
    set_user_processing
)
from ..utils import format_sale_summary


def register_sales_handlers(bot, data_manager):
    """ثبت هندلرهای فروش"""
    
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
            
            text = f"🧾 فروش شماره {sale['id']}\n"
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
