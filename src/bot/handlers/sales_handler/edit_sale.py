"""
هندلرهای ویرایش فروش
"""

from ...keyboards import back_button, cancel_button
from ...states.state import (
    set_user_state,
    get_user_data,
    is_user_processing,
    set_user_processing
)
from ....services.sale_services import SalesService


class EditSale:
    """مدیریت ویرایش فروش"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.sales_service = SalesService(data_manager)
    
    def register(self):
        """ثبت هندلرهای ویرایش فروش"""
        self._register_edit_sale_handlers()
    
    def _register_edit_sale_handlers(self):
        """هندلرهای ویرایش فروش"""
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("edit_sale_"))
        def edit_sale_start(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                sale_id = int(call.data.split("_")[2])
                
                # استفاده از ولیدیشن برای بررسی وجود فروش
                validation = self.sales_service.sale_validator.validate_sale_exists(sale_id)
                
                if not validation['is_valid']:
                    self.bot.send_message(user_id, "❌ فروش یافت نشد.", reply_markup=back_button("sales"))
                    return
                
                sale = validation['sale']
                get_user_data(user_id)['selected_sale_id'] = sale_id
                get_user_data(user_id)['sale_data'] = sale.copy()
                set_user_state(user_id, 'edit_sale_quantity')
                
                msg = self.bot.send_message(user_id, f"🔢 تعداد جدید را وارد کنید (فعلی: {sale['quantity']}):", reply_markup=cancel_button())
                self.bot.register_next_step_handler(msg, self._process_edit_sale_quantity)
            finally:
                set_user_processing(user_id, False)
    
    def _process_edit_sale_quantity(self, message):
        """پردازش ویرایش تعداد فروش"""
        user_id = message.chat.id
        quantity = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_quantity(quantity, 999999)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_edit_sale_quantity)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['quantity'] = validation['quantity']
        set_user_state(user_id, 'edit_sale_price')
        
        msg = self.bot.send_message(user_id, f"💵 کل مبلغ فروش جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['total_sale_price']}):", reply_markup=cancel_button())
        self.bot.register_next_step_handler(msg, self._process_edit_sale_price)
    
    def _process_edit_sale_price(self, message):
        """پردازش ویرایش قیمت فروش"""
        user_id = message.chat.id
        price = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_price(price)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_edit_sale_price)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['total_sale_price'] = validation['price']
        user_data_dict['sale_data']['sale_price'] = validation['price'] / user_data_dict['sale_data']['quantity']
        set_user_state(user_id, 'edit_sale_cost')
        
        msg = self.bot.send_message(user_id, f"💸 کل مبلغ خرید جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['total_cost']}):", reply_markup=cancel_button())
        self.bot.register_next_step_handler(msg, self._process_edit_sale_cost)
    
    def _process_edit_sale_cost(self, message):
        """پردازش ویرایش هزینه خرید"""
        user_id = message.chat.id
        cost = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_cost(cost)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_edit_sale_cost)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['total_cost'] = validation['cost']
        set_user_state(user_id, 'edit_sale_extra_cost')
        
        msg = self.bot.send_message(user_id, f"🏷️ هزینه‌های جانبی جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['extra_cost']}):", reply_markup=cancel_button())
        self.bot.register_next_step_handler(msg, self._process_edit_sale_extra_cost)
    
    def _process_edit_sale_extra_cost(self, message):
        """پردازش ویرایش هزینه‌های جانبی"""
        user_id = message.chat.id
        extra_cost = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_extra_cost(extra_cost)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_edit_sale_extra_cost)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['extra_cost'] = validation['extra_cost']
        set_user_state(user_id, 'edit_sale_date')
        
        msg = self.bot.send_message(user_id, f"📅 تاریخ جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['date']}):", reply_markup=cancel_button())
        self.bot.register_next_step_handler(msg, self._process_edit_sale_date)
    
    def _process_edit_sale_date(self, message):
        """پردازش ویرایش تاریخ فروش"""
        user_id = message.chat.id
        date = message.text
        
        # استفاده از ولیدیشن سرویس
        validation = self.sales_service.input_validator.validate_sale_date(date)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, validation['error_message'], reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_edit_sale_date)
            return
        
        user_data_dict = get_user_data(user_id)
        sale_data = user_data_dict['sale_data']
        sale_data['date'] = validation['date']
        
        sale_id = user_data_dict['selected_sale_id']
        
        # استفاده از سرویس برای بروزرسانی فروش
        result = self.sales_service.update_sale(sale_id, sale_data)
        
        if result['success']:
            self.bot.send_message(user_id, "✅ فروش به‌روزرسانی شد.", reply_markup=back_button("sales"))
        else:
            self.bot.send_message(user_id, result['error_message'], reply_markup=back_button("sales"))
        
        set_user_state(user_id, 'view_sales')
