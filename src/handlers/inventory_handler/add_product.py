"""
هندلرهای اضافه کردن محصول
"""

from ...keyboards import back_button
from ..state import (
    set_user_state,
    get_user_data,
    is_user_processing,
    set_user_processing
)


class AddProduct:
    """مدیریت اضافه کردن محصول"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
    def register(self):
        """ثبت هندلرهای اضافه کردن محصول"""
        self._register_add_product_handlers()
    
    def _register_add_product_handlers(self):
        """هندلرهای اضافه کردن محصول"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "add_product")
        def add_product_start(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                set_user_state(user_id, 'add_product_name')
                
                msg = self.bot.send_message(user_id, "📝 لطفاً نام محصول را وارد کنید:")
                self.bot.register_next_step_handler(msg, self._process_product_name)
            finally:
                set_user_processing(user_id, False)
    
    def _process_product_name(self, message):
        """دریافت نام محصول"""
        user_id = message.chat.id
        product_name = message.text.strip()
        
        if not product_name:
            msg = self.bot.send_message(user_id, "❌ نام محصول نمی‌تواند خالی باشد. دوباره تلاش کنید:")
            self.bot.register_next_step_handler(msg, self._process_product_name)
            return
        
        get_user_data(user_id)['product_name'] = product_name
        set_user_state(user_id, 'add_product_qty')
        
        msg = self.bot.send_message(user_id, "📦 لطفاً موجودی اولیه را وارد کنید (عدد):")
        self.bot.register_next_step_handler(msg, self._process_product_quantity)
    
    def _process_product_quantity(self, message):
        """دریافت موجودی محصول"""
        user_id = message.chat.id
        user_data_dict = get_user_data(user_id)
        
        try:
            quantity = int(message.text.strip())
            if quantity < 0:
                raise ValueError
        except ValueError:
            msg = self.bot.send_message(user_id, "❌ لطفاً عدد صحیح و مثبت وارد کنید:")
            self.bot.register_next_step_handler(msg, self._process_product_quantity)
            return
        
        product_name = user_data_dict.get('product_name')
        if not product_name:
            msg = self.bot.send_message(user_id, "❌ خطا: نام محصول یافت نشد. لطفاً دوباره تلاش کنید.")
            self.bot.register_next_step_handler(msg, self._process_product_name)
            return
        
        self.data_manager.add_product(product_name, quantity)
        
        self.bot.send_message(
            user_id,
            f"✅ محصول '{product_name}' با موجودی {quantity} عدد اضافه شد.",
            reply_markup=back_button()
        )
        
        set_user_state(user_id, 'inventory_menu')
