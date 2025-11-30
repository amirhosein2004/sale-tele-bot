"""
مدیریت global برای دکمه Cancel
"""

from ...states.state import set_user_state, clear_user_data
from ...keyboards import main_menu_keyboard


class CancelOperations:
    """مدیریت عملیات های کنسل"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
    def register(self):
        """ثبت هندلرها"""
        self._register_global_cancel_handler()

    def _register_global_cancel_handler(self):
        """
        ثبت یک callback_query_handler global برای دکمه Cancel
        این هندلر تمام درخواست‌های Cancel را بررسی می‌کند
        
        Args:
            bot: نمونه ربات
        """
        @self.bot.callback_query_handler(func=lambda call: call.data == "cancel_operation")
        def cancel_operation(call):
            user_id = call.message.chat.id
            
            # لغو register_next_step_handler
            self.bot.clear_step_handler_by_chat_id(user_id)
            
            set_user_state(user_id, 'main_menu')
            clear_user_data(user_id)
            
            
            self.bot.edit_message_text(
                "❌ عملیات لغو شد.\n\nبه منوی اصلی برگشتید.",
                user_id,
                call.message.message_id,
                reply_markup=main_menu_keyboard()
            )
            
            self.bot.answer_callback_query(call.id, "عملیات لغو شد ✅", show_alert=False)
