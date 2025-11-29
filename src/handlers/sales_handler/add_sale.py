"""
هندلرهای اضافه کردن فروش
"""

from ...keyboards import products_list_keyboard, back_button
from ..state import (
    set_user_state,
    get_user_state,
    get_user_data,
    clear_user_data,
    is_user_processing,
    set_user_processing
)
from ...services.sale_services import SalesService
from ...services.inventory_services import InventoryService


class AddSale:
    """مدیریت اضافه کردن فروش"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.sales_service = SalesService(data_manager)
        self.inventory_service = InventoryService(data_manager)
    
    def register(self):
        """ثبت هندلرهای اضافه کردن فروش"""
        self._register_add_sale_handlers()
    
    def _register_add_sale_handlers(self):
        """هندلرهای اضافه کردن فروش جدید"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "add_sale")
        def add_sale_start(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                # استفاده از سرویس برای دریافت وضعیت محصولات
                status = self.inventory_service.get_available_products_with_status()
                
                if not status['has_products']:
                    self.bot.send_message(
                        user_id,
                        status['message'],
                        reply_markup=back_button()
                    )
                    return
                
                set_user_state(user_id, 'add_sale_product')
                clear_user_data(user_id)
                
                available_products = status['available_products']
                products_text = "📦 *محصولات موجود برای فروش:*\n\n"
                for product in available_products:
                    status_icon = "✅" if product['quantity'] > 0 else "❌"
                    products_text += f"{status_icon} {product['name']} - موجودی: {product['quantity']} عدد\n"
                
                self.bot.edit_message_text(
                    products_text + "\n\n📝 محصول مورد نظر را از لیست زیر انتخاب کنید:",
                    user_id,
                    call.message.message_id,
                    reply_markup=products_list_keyboard(available_products, for_sale=True),
                    parse_mode="Markdown"
                )
            finally:
                set_user_processing(user_id, False)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("select_product_") and get_user_state(call.message.chat.id) == 'add_sale_product')
        def select_product_for_sale(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                product_id = int(call.data.split("_")[2])
                product = self.data_manager.get_product(product_id)
                
                if not product:
                    self.bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button())
                    return
                
                if product['quantity'] <= 0:
                    self.bot.send_message(
                        user_id, 
                        f"❌ محصول '{product['name']}' موجودی ندارد.\n\nلطفاً محصول دیگری انتخاب کنید یا ابتدا موجودی را تکمیل کنید.",
                        reply_markup=back_button()
                    )
                    return
                
                get_user_data(user_id)['product_name'] = product['name']
                get_user_data(user_id)['product_id'] = product_id
                get_user_data(user_id)['available_quantity'] = product['quantity']
                set_user_state(user_id, 'add_sale_quantity')
                
                msg = self.bot.send_message(
                    user_id, 
                    f"🔢 تعداد فروش را وارد کنید:\n\n📦 موجودی فعلی: {product['quantity']} عدد\n💡 حداکثر قابل فروش: {product['quantity']} عدد"
                )
                self.bot.register_next_step_handler(msg, self._process_sale_quantity)
            finally:
                set_user_processing(user_id, False)
    
    def _process_sale_quantity(self, message):
        """دریافت تعداد فروش"""
        user_id = message.chat.id
        user_data_dict = get_user_data(user_id)
        available_qty = user_data_dict.get('available_quantity', 0)
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_quantity(message.text.strip(), available_qty)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'])
            self.bot.register_next_step_handler(msg, self._process_sale_quantity)
            return
        
        quantity = validation['quantity']
        product_id = user_data_dict['product_id']
        
        # بررسی نهایی موجودی
        if not self.data_manager.check_inventory(product_id, quantity):
            current_product = self.data_manager.get_product(product_id)
            current_qty = current_product['quantity'] if current_product else 0
            msg = self.bot.send_message(
                user_id, 
                f"❌ موجودی تغییر کرده است!\n\n📦 موجودی فعلی: {current_qty} عدد\n\nلطفاً تعداد جدید را وارد کنید:"
            )
            user_data_dict['available_quantity'] = current_qty
            self.bot.register_next_step_handler(msg, self._process_sale_quantity)
            return
        
        user_data_dict['quantity'] = quantity
        set_user_state(user_id, 'add_sale_price')
        
        msg = self.bot.send_message(user_id, "💵 کل مبلغ فروش را وارد کنید:")
        self.bot.register_next_step_handler(msg, self._process_sale_price)
    
    def _process_sale_price(self, message):
        """دریافت قیمت فروش"""
        user_id = message.chat.id
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_price(message.text.strip())
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'])
            self.bot.register_next_step_handler(msg, self._process_sale_price)
            return
        
        get_user_data(user_id)['total_sale_price'] = validation['price']
        set_user_state(user_id, 'add_sale_cost')
        
        msg = self.bot.send_message(user_id, "💸 کل مبلغ خرید (هزینه تهیه) را وارد کنید:")
        self.bot.register_next_step_handler(msg, self._process_sale_cost)
    
    def _process_sale_cost(self, message):
        """دریافت هزینه خرید"""
        user_id = message.chat.id
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_cost(message.text.strip())
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'])
            self.bot.register_next_step_handler(msg, self._process_sale_cost)
            return
        
        get_user_data(user_id)['total_cost'] = validation['cost']
        set_user_state(user_id, 'add_sale_extra_cost')
        
        msg = self.bot.send_message(user_id, "🏷️ هزینه‌های جانبی را وارد کنید (مثل حمل‌ونقل):")
        self.bot.register_next_step_handler(msg, self._process_extra_cost)
    
    def _process_extra_cost(self, message):
        """دریافت هزینه‌های جانبی"""
        user_id = message.chat.id
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_extra_cost(message.text.strip())
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'])
            self.bot.register_next_step_handler(msg, self._process_extra_cost)
            return
        
        get_user_data(user_id)['extra_cost'] = validation['extra_cost']
        set_user_state(user_id, 'add_sale_date')
        
        msg = self.bot.send_message(user_id, "📅 تاریخ فروش را وارد کنید (مثال: 1403/09/29):")
        self.bot.register_next_step_handler(msg, self._process_sale_date)
    
    def _process_sale_date(self, message):
        """دریافت تاریخ فروش"""
        user_id = message.chat.id
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_date(message.text.strip())
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'])
            self.bot.register_next_step_handler(msg, self._process_sale_date)
            return
        
        user_data_dict = get_user_data(user_id)
        product_id = user_data_dict['product_id']
        quantity = user_data_dict['quantity']
        
        # ساخت داده‌های فروش
        sale_data = {
            'product_id': product_id,
            'product_name': user_data_dict['product_name'],
            'quantity': quantity,
            'sale_price': user_data_dict['total_sale_price'] / quantity,
            'total_sale_price': user_data_dict['total_sale_price'],
            'total_cost': user_data_dict['total_cost'],
            'extra_cost': user_data_dict['extra_cost'],
            'net_profit': user_data_dict['total_sale_price'] - user_data_dict['total_cost'] - user_data_dict['extra_cost'],
            'date': validation['date']
        }
        
        # استفاده از سرویس برای ایجاد فروش
        result = self.sales_service.create_sale(sale_data)
        
        if result['success']:
            self.bot.send_message(user_id, result['summary'], parse_mode="Markdown", reply_markup=back_button())
        else:
            self.bot.send_message(user_id, result['error_message'], reply_markup=back_button())
        
        set_user_state(user_id, 'sales_menu')
