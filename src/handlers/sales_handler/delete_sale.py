"""
هندلرهای حذف فروش
"""

from ...keyboards import back_button, confirmation_keyboard
from ...states.state import (
    is_user_processing,
    set_user_processing
)
from ...services.sale_services import SalesService


class DeleteSale:
    """مدیریت حذف فروش"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.sales_service = SalesService(data_manager)
    
    def register(self):
        """ثبت هندلرهای حذف فروش"""
        self._register_delete_sale_handler()
    
    def _register_delete_sale_handler(self):
        """هندلر حذف فروش"""
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("delete_sale_"))
        def delete_sale(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                sale_id = int(call.data.split("_")[2])
                
                # استفاده از ولیدیشن برای بررسی وجود فروش
                validation = self.sales_service.sale_validator.validate_sale_exists(sale_id)
                
                if validation['is_valid']:
                    sale = validation['sale']
                    self.bot.edit_message_text(
                        f"⚠️ آیا مطمئن هستید که می‌خواهید فروش '{sale['product_name']}' را حذف کنید؟\n\nاین عمل قابل بازگشت نیست!",
                        user_id,
                        call.message.message_id,
                        reply_markup=confirmation_keyboard("delete_sale", sale_id)
                    )
                else:
                    self.bot.send_message(user_id, "❌ فروش یافت نشد.", reply_markup=back_button("sales"))
            finally:
                set_user_processing(user_id, False)
