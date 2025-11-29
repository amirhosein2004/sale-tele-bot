"""
هندلر مشاهده موجودی محصولات
"""

from ...keyboards import back_button
from ...services.inventory_services import InventoryService


class ViewInventory:
    """مدیریت مشاهده موجودی"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.inventory_service = InventoryService(data_manager)
    
    def register(self):
        """ثبت هندلر مشاهده موجودی"""
        self._register_view_inventory_handler()
    
    def _register_view_inventory_handler(self):
        """هندلر مشاهده لیست محصولات"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "view_inventory")
        def view_inventory(call):
            user_id = call.message.chat.id
            
            # استفاده از سرویس برای دریافت و فرمت‌بندی محصولات
            products = self.data_manager.get_all_products()
            inventory_text = self.inventory_service.format_products_list(products)
            
            self.bot.send_message(
                user_id,
                inventory_text,
                parse_mode="Markdown",
                reply_markup=back_button("inventory")
            )
