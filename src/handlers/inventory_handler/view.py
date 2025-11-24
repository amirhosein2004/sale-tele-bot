"""
هندلر مشاهده موجودی محصولات
"""

from ...keyboards import back_button


class ViewInventory:
    """مدیریت مشاهده موجودی"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
    def register(self):
        """ثبت هندلر مشاهده موجودی"""
        self._register_view_inventory_handler()
    
    def _register_view_inventory_handler(self):
        """هندلر مشاهده لیست محصولات"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "view_inventory")
        def view_inventory(call):
            user_id = call.message.chat.id
            inventory_text = self.data_manager.get_products_text()
            
            self.bot.send_message(
                user_id,
                inventory_text,
                parse_mode="Markdown",
                reply_markup=back_button()
            )
