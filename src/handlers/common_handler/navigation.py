"""
ماژول ناوبری و منوهای سریع
شامل: pagination، quick actions، share menu، disabled button
"""

from ...keyboards import (
    quick_actions_keyboard,
    share_keyboard
)
from ...utils import (
    QUICK_ACTIONS_TITLE,
    SHARE_MENU_TITLE,
    DISABLED_BUTTON_MESSAGE,
)


class NavigationMenu:
    """مدیریت منوهای ناوبری و عملیات سریع"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
    def register(self):
        """ثبت هندلرهای ناوبری"""
        self._register_quick_actions_handler()
        self._register_share_menu_handler()
        self._register_disabled_button_handler()
    
    def _register_quick_actions_handler(self):
        """منوی عملیات سریع"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "quick_actions")
        def quick_actions_menu(call):
            user_id = call.message.chat.id
            self._show_quick_actions(user_id, call.message.message_id, edit=True)
    
    def _show_quick_actions(self, user_id, message_id=None, edit=False):
        """نمایش منوی عملیات سریع"""
        if edit and message_id:
            self.bot.edit_message_text(
                QUICK_ACTIONS_TITLE,
                user_id,
                message_id,
                reply_markup=quick_actions_keyboard()
            )
        else:
            self.bot.send_message(
                user_id,
                QUICK_ACTIONS_TITLE,
                reply_markup=quick_actions_keyboard()
            )
    
    def _register_share_menu_handler(self):
        """منوی اشتراک‌گذاری"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "share_menu")
        def share_menu(call):
            user_id = call.message.chat.id
            self._show_share_menu(user_id, call.message.message_id, edit=True)
    
    def _show_share_menu(self, user_id, message_id=None, edit=False):
        """نمایش منوی اشتراک‌گذاری"""
        if edit and message_id:
            self.bot.edit_message_text(
                SHARE_MENU_TITLE,
                user_id,
                message_id,
                reply_markup=share_keyboard()
            )
        else:
            self.bot.send_message(
                user_id,
                SHARE_MENU_TITLE,
                reply_markup=share_keyboard()
            )
    
    def _register_disabled_button_handler(self):
        """مدیریت دکمه‌های غیرفعال"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "disabled")
        def disabled_button(call):
            self.bot.answer_callback_query(
                call.id, 
                DISABLED_BUTTON_MESSAGE, 
                show_alert=True
            )
