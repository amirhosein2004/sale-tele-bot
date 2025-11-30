"""
هندلرهای اضافه کردن فروش
"""

from ...keyboards import (
    back_button,
    cancel_button,
    products_list_keyboard_with_pagination,
)
from ...states.state import (
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
    
    ITEMS_PER_PAGE = 20
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.sales_service = SalesService(data_manager)
        self.inventory_service = InventoryService(data_manager)
    
    def register(self):
        """ثبت هندلرهای اضافه کردن فروش"""
        self._register_add_sale_handlers()
        self._register_pagination_handler()
    
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
                # دریافت صفحه اول از سرویس
                page_data = self.sales_service.get_products_for_sale_page(page=1, items_per_page=self.ITEMS_PER_PAGE)
                
                if not page_data['has_products']:
                    self.bot.send_message(
                        user_id,
                        page_data['text'],
                        reply_markup=back_button("sales")
                    )
                    return
                
                set_user_state(user_id, 'add_sale_product')
                clear_user_data(user_id)
                
                # ساخت کیبورد با صفحه‌بندی
                keyboard = products_list_keyboard_with_pagination(
                    page_data['products'],
                    page_data['page'],
                    page_data['total_pages'],
                    for_sale=True
                )
                
                self.bot.edit_message_text(
                    page_data['text'],
                    user_id,
                    call.message.message_id,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            finally:
                set_user_processing(user_id, False)
        
        @self.bot.callback_query_handler(
            func=lambda call: call.data.startswith("select_product_")
            and get_user_state(call.message.chat.id) == 'add_sale_product'
        )
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
                    self.bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button("sales"))
                    return
                
                if int(product['quantity']) <= 0:
                    self.bot.send_message(
                        user_id, 
                        f"❌ محصول '{product['name']}' موجودی ندارد.\n\nلطفاً محصول دیگری انتخاب کنید یا ابتدا موجودی را تکمیل کنید.",
                        reply_markup=back_button("sales")
                    )
                    return
                
                get_user_data(user_id)['product_name'] = product['name']
                get_user_data(user_id)['product_id'] = product_id
                get_user_data(user_id)['available_quantity'] = product['quantity']
                set_user_state(user_id, 'add_sale_quantity')
                
                msg = self.bot.send_message(
                    user_id, 
                    f"🔢 تعداد فروش را وارد کنید:\n\n📦 موجودی فعلی: {product['quantity']} عدد\n💡 حداکثر قابل فروش: {product['quantity']} عدد",
                    reply_markup=cancel_button()
                )
                self.bot.register_next_step_handler(msg, self._process_sale_quantity)
            finally:
                set_user_processing(user_id, False)
    
    def _process_sale_quantity(self, message):
        """دریافت تعداد فروش"""
        user_id = message.chat.id
        user_data_dict = get_user_data(user_id)
        available_qty = user_data_dict.get('available_quantity', 0)
        quantity = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_quantity(quantity, available_qty)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_sale_quantity)
            return
        
        validated_quantity = validation['quantity']
        product_id = user_data_dict['product_id']
        
        # بررسی نهایی موجودی
        if not self.data_manager.check_inventory(product_id, validated_quantity):
            current_product = self.data_manager.get_product(product_id)
            current_qty = current_product['quantity'] if current_product else 0
            msg = self.bot.send_message(
                user_id, 
                f"❌ موجودی تغییر کرده است!\n\n📦 موجودی فعلی: {current_qty} عدد\n\nلطفاً تعداد جدید را وارد کنید:",
                reply_markup=cancel_button()
            )
            user_data_dict['available_quantity'] = current_qty
            self.bot.register_next_step_handler(msg, self._process_sale_quantity)
            return
        
        user_data_dict['quantity'] = validated_quantity
        set_user_state(user_id, 'add_sale_price')
        
        msg = self.bot.send_message(user_id, "💵 کل مبلغ فروش را وارد کنید:", reply_markup=cancel_button())
        self.bot.register_next_step_handler(msg, self._process_sale_price)
    
    def _process_sale_price(self, message):
        """دریافت قیمت فروش"""
        user_id = message.chat.id
        price = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_price(price)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_sale_price)
            return
        
        get_user_data(user_id)['total_sale_price'] = validation['price']
        set_user_state(user_id, 'add_sale_cost')
        
        msg = self.bot.send_message(user_id, "💸 کل مبلغ خرید (هزینه تهیه) را وارد کنید:", reply_markup=cancel_button())
        self.bot.register_next_step_handler(msg, self._process_sale_cost)
    
    def _process_sale_cost(self, message):
        """دریافت هزینه خرید"""
        user_id = message.chat.id
        cost = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_cost(cost)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_sale_cost)
            return
        
        get_user_data(user_id)['total_cost'] = validation['cost']
        set_user_state(user_id, 'add_sale_extra_cost')
        
        msg = self.bot.send_message(user_id, "🏷️ هزینه‌های جانبی را وارد کنید (مثل حمل‌ونقل):", reply_markup=cancel_button())
        self.bot.register_next_step_handler(msg, self._process_extra_cost)
    
    def _process_extra_cost(self, message):
        """دریافت هزینه‌های جانبی"""
        user_id = message.chat.id
        extra_cost = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_extra_cost(extra_cost)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_extra_cost)
            return
        
        get_user_data(user_id)['extra_cost'] = validation['extra_cost']
        set_user_state(user_id, 'add_sale_date')
        
        msg = self.bot.send_message(user_id, "📅 تاریخ فروش را وارد کنید (مثال: 1403/09/29):", reply_markup=cancel_button())
        self.bot.register_next_step_handler(msg, self._process_sale_date)
    
    def _process_sale_date(self, message):
        """دریافت تاریخ فروش"""
        user_id = message.chat.id
        date = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_date(date)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
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
            self.bot.send_message(user_id, result['summary'], parse_mode="Markdown", reply_markup=back_button("sales"))
        else:
            self.bot.send_message(user_id, result['error_message'], reply_markup=back_button("sales"))
        
        set_user_state(user_id, 'sales_menu')
    
    def _register_pagination_handler(self):
        """هندلر صفحه‌بندی محصولات برای فروش"""
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("sale_products_page_"))
        def handle_sale_products_pagination(call):
            user_id = call.message.chat.id
            message_id = call.message.message_id
            page = int(call.data.split("_")[-1])
            
            # دریافت صفحه از سرویس
            page_data = self.sales_service.get_products_for_sale_page(page=page, items_per_page=self.ITEMS_PER_PAGE)
            
            # ساخت کیبورد
            keyboard = products_list_keyboard_with_pagination(
                page_data['products'],
                page_data['page'],
                page_data['total_pages'],
                for_sale=True
            )
            
            self.bot.edit_message_text(
                page_data['text'],
                user_id,
                message_id,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
