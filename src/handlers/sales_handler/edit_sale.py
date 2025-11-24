"""
هندلرهای ویرایش فروش
"""

from ...keyboards import back_button
from ..state import (
    set_user_state,
    get_user_data,
    is_user_processing,
    set_user_processing
)


class EditSale:
    """مدیریت ویرایش فروش"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
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
                sale = self.data_manager.get_sale(sale_id)
                
                if not sale:
                    self.bot.send_message(user_id, "❌ فروش یافت نشد.", reply_markup=back_button())
                    return
                
                get_user_data(user_id)['selected_sale_id'] = sale_id
                get_user_data(user_id)['sale_data'] = sale.copy()
                set_user_state(user_id, 'edit_sale_quantity')
                
                msg = self.bot.send_message(user_id, f"🔢 تعداد جدید را وارد کنید (فعلی: {sale['quantity']}):")
                self.bot.register_next_step_handler(msg, self._process_edit_sale_quantity)
            finally:
                set_user_processing(user_id, False)
    
    def _process_edit_sale_quantity(self, message):
        """پردازش ویرایش تعداد فروش"""
        user_id = message.chat.id
        
        try:
            quantity = int(message.text.strip())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            msg = self.bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            self.bot.register_next_step_handler(msg, self._process_edit_sale_quantity)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['quantity'] = quantity
        set_user_state(user_id, 'edit_sale_price')
        
        msg = self.bot.send_message(user_id, f"💵 کل مبلغ فروش جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['total_sale_price']}):")
        self.bot.register_next_step_handler(msg, self._process_edit_sale_price)
    
    def _process_edit_sale_price(self, message):
        """پردازش ویرایش قیمت فروش"""
        user_id = message.chat.id
        
        try:
            sale_price = float(message.text.strip())
            if sale_price <= 0:
                raise ValueError
        except ValueError:
            msg = self.bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            self.bot.register_next_step_handler(msg, self._process_edit_sale_price)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['total_sale_price'] = sale_price
        user_data_dict['sale_data']['sale_price'] = sale_price / user_data_dict['sale_data']['quantity']
        set_user_state(user_id, 'edit_sale_cost')
        
        msg = self.bot.send_message(user_id, f"💸 کل مبلغ خرید جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['total_cost']}):")
        self.bot.register_next_step_handler(msg, self._process_edit_sale_cost)
    
    def _process_edit_sale_cost(self, message):
        """پردازش ویرایش هزینه خرید"""
        user_id = message.chat.id
        
        try:
            cost = float(message.text.strip())
            if cost < 0:
                raise ValueError
        except ValueError:
            msg = self.bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            self.bot.register_next_step_handler(msg, self._process_edit_sale_cost)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['total_cost'] = cost
        set_user_state(user_id, 'edit_sale_extra_cost')
        
        msg = self.bot.send_message(user_id, f"🏷️ هزینه‌های جانبی جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['extra_cost']}):")
        self.bot.register_next_step_handler(msg, self._process_edit_sale_extra_cost)
    
    def _process_edit_sale_extra_cost(self, message):
        """پردازش ویرایش هزینه‌های جانبی"""
        user_id = message.chat.id
        
        try:
            extra_cost = float(message.text.strip())
            if extra_cost < 0:
                raise ValueError
        except ValueError:
            msg = self.bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            self.bot.register_next_step_handler(msg, self._process_edit_sale_extra_cost)
            return
        
        user_data_dict = get_user_data(user_id)
        user_data_dict['sale_data']['extra_cost'] = extra_cost
        set_user_state(user_id, 'edit_sale_date')
        
        msg = self.bot.send_message(user_id, f"📅 تاریخ جدید را وارد کنید (فعلی: {user_data_dict['sale_data']['date']}):")
        self.bot.register_next_step_handler(msg, self._process_edit_sale_date)
    
    def _process_edit_sale_date(self, message):
        """پردازش ویرایش تاریخ فروش"""
        user_id = message.chat.id
        sale_date = message.text.strip()
        
        if not sale_date:
            msg = self.bot.send_message(user_id, "❌ تاریخ نمی‌تواند خالی باشد:")
            self.bot.register_next_step_handler(msg, self._process_edit_sale_date)
            return
        
        user_data_dict = get_user_data(user_id)
        sale_data = user_data_dict['sale_data']
        sale_data['date'] = sale_date
        
        sale_data['net_profit'] = sale_data['total_sale_price'] - sale_data['total_cost'] - sale_data['extra_cost']
        
        sale_id = user_data_dict['selected_sale_id']
        self.data_manager.update_sale(sale_id, sale_data)
        
        self.bot.send_message(user_id, "✅ فروش به‌روزرسانی شد.", reply_markup=back_button())
        set_user_state(user_id, 'view_sales')
