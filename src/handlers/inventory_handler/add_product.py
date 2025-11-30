"""
هندلرهای اضافه کردن محصول
"""

from ...keyboards import back_button, cancel_button
from ...states.state import (
    set_user_state,
    get_user_data,
    is_user_processing,
    set_user_processing
)
from ...services.inventory_services import InventoryService


class AddProduct:
    """مدیریت اضافه کردن محصول"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.inventory_service = InventoryService(data_manager)
    
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
                
                msg = self.bot.send_message(user_id, "📝 لطفاً نام محصول را وارد کنید:", reply_markup=cancel_button())
                self.bot.register_next_step_handler(msg, self._process_product_name)
            finally:
                set_user_processing(user_id, False)
    
    def _process_product_name(self, message):
        """دریافت نام محصول"""
        user_id = message.chat.id
        product_name = message.text
        
        # ولیدیشن نام محصول
        validation = self.inventory_service.product_validator.validate_product_name(product_name)
        
        if not validation['is_valid']:
            msg = self.bot.send_message(user_id, f"{validation['error_message']} دوباره تلاش کنید:", reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_product_name)
            return
        
        # ذخیره نام ولیدیشن‌شده
        get_user_data(user_id)['product_name'] = validation['name']
        set_user_state(user_id, 'add_product_qty')
        
        msg = self.bot.send_message(user_id, "📦 لطفاً موجودی اولیه را وارد کنید (عدد):", reply_markup=cancel_button())
        self.bot.register_next_step_handler(msg, self._process_product_quantity)
    
    def _process_product_quantity(self, message):
        """دریافت موجودی محصول"""
        user_id = message.chat.id
        user_data_dict = get_user_data(user_id)
        product_name = user_data_dict.get('product_name')
        quantity = message.text
        
        # ولیدیشن موجودی
        quantity_validation = self.inventory_service.product_validator.validate_product_quantity(quantity)
        
        if not quantity_validation['is_valid']:
            msg = self.bot.send_message(user_id, f"{quantity_validation['error_message']} دوباره تلاش کنید:", reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_product_quantity)
            return
        
        # استفاده از سرویس برای ایجاد محصول (داده‌های ولیدیشن‌شده)
        result = self.inventory_service.create_product(product_name, quantity_validation['quantity'])
        
        if not result['success']:
            msg = self.bot.send_message(user_id, f"{result['error_message']} دوباره تلاش کنید:", reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_product_quantity)
            return
        
        self.bot.send_message(
            user_id,
            f"✅ محصول '{result['product_name']}' با موجودی {result['quantity']} عدد اضافه شد.",
            reply_markup=back_button("inventory")
        )
        
        set_user_state(user_id, 'inventory_menu')
