"""
هندلرهای حذف محصول
"""

from ...keyboards import (
    back_button,
    confirmation_keyboard
)
from ..state import (
    is_user_processing,
    set_user_processing
)
from ...services.inventory_services import InventoryService


class DeleteProduct:
    """مدیریت حذف محصول"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.inventory_service = InventoryService(data_manager)
    
    def register(self):
        """ثبت هندلرهای حذف محصول"""
        self._register_delete_product_handler()
    
    def _register_delete_product_handler(self):
        """هندلر حذف محصول"""
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("delete_product_"))
        def delete_product(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                product_id = int(call.data.split("_")[2])
                
                # استفاده از ولیدیتور برای بررسی وجود محصول
                validation = self.inventory_service.product_validator.validate_product_exists(product_id)
                
                if validation['is_valid']:
                    product = validation['product']
                    self.bot.edit_message_text(
                        f"⚠️ آیا مطمئن هستید که می‌خواهید محصول '{product['name']}' را حذف کنید؟\n\nاین عمل قابل بازگشت نیست!",
                        user_id,
                        call.message.message_id,
                        reply_markup=confirmation_keyboard("delete_product", product_id)
                    )
                else:
                    self.bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button())
            finally:
                set_user_processing(user_id, False)
