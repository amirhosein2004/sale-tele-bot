"""
هندلرهای منوی موجودی محصولات
"""

from ...keyboards import inventory_menu_keyboard
from ..state import set_user_state


class InventoryMenu:
    """مدیریت منوی موجودی"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
    def register(self):
        """ثبت هندلرهای منوی موجودی"""
        self._register_inventory_menu()
        self._register_back_to_inventory()
    
    def _register_inventory_menu(self):
        """هندلر منوی موجودی"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "inventory_menu")
        def inventory_menu(call):
            user_id = call.message.chat.id
            set_user_state(user_id, 'inventory_menu')
            
            self.bot.edit_message_text(
                "📦 منوی موجودی محصولات",
                user_id,
                call.message.message_id,
                reply_markup=inventory_menu_keyboard()
            )
    
    def _register_back_to_inventory(self):
        """هندلر بازگشت به منوی موجودی"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "back_to_inventory")
        def back_to_inventory(call):
            user_id = call.message.chat.id
            set_user_state(user_id, 'inventory_menu')
            
            self.bot.edit_message_text(
                "📦 منوی موجودی محصولات",
                user_id,
                call.message.message_id,
                reply_markup=inventory_menu_keyboard()
            )
