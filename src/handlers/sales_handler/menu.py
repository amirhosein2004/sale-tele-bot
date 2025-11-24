"""
هندلرهای منوی فروش
"""

from ...keyboards import sales_menu_keyboard
from ..state import set_user_state


class SalesMenu:
    """مدیریت منوی فروش"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
    def register(self):
        """ثبت هندلرهای منوی فروش"""
        self._register_sales_menu()
        self._register_back_to_sales()
    
    def _register_sales_menu(self):
        """هندلر منوی فروش"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "sales_menu")
        def sales_menu(call):
            user_id = call.message.chat.id
            set_user_state(user_id, 'sales_menu')
            
            self.bot.edit_message_text(
                "💳 منوی فروش محصولات",
                user_id,
                call.message.message_id,
                reply_markup=sales_menu_keyboard()
            )
    
    def _register_back_to_sales(self):
        """هندلر بازگشت به منوی فروش"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "back_to_sales")
        def back_to_sales(call):
            user_id = call.message.chat.id
            set_user_state(user_id, 'sales_menu')
            
            self.bot.edit_message_text(
                "💳 منوی فروش محصولات",
                user_id,
                call.message.message_id,
                reply_markup=sales_menu_keyboard()
            )
