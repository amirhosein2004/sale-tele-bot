"""
ماژول منطق تایید و حذف
شامل: تأیید عملیات، حذف محصول، حذف فروش، لغو
"""

from ...keyboards import back_button, main_menu_keyboard
from ..state import (
    set_user_state,
    is_user_processing,
    set_user_processing
)
from ...utils import (
    ERROR_MESSAGE,
    NOT_FOUND_MESSAGE,
    CANCEL_MESSAGE,
    PROCESSING_MESSAGE
)


class ConfirmationManager:
    """مدیریت تأیید و حذف عملیات"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
    def register(self):
        """ثبت هندلرهای تأیید و حذف"""
        self._register_confirmation_handler()
        self._register_cancel_handler()
    
    def _register_confirmation_handler(self):
        """مدیریت تأییدیه‌ها"""
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
        def handle_confirmation(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, PROCESSING_MESSAGE, show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                parts = call.data.split("_")
                if len(parts) < 4:
                    self.bot.answer_callback_query(call.id, ERROR_MESSAGE, show_alert=True)
                    return
                
                action_type = parts[1]
                item_type = parts[2]
                action = f"{action_type}_{item_type}"
                
                try:
                    item_id = int(parts[3])
                except ValueError:
                    self.bot.answer_callback_query(call.id, ERROR_MESSAGE, show_alert=True)
                    return
                
                if action == "delete_product":
                    self._handle_delete_product(user_id, call, item_id)
                elif action == "delete_sale":
                    self._handle_delete_sale(user_id, call, item_id)
                
                set_user_state(user_id, 'main_menu')
            finally:
                set_user_processing(user_id, False)
    
    def _handle_delete_product(self, user_id, call, product_id):
        """حذف محصول"""
        product = self.data_manager.get_product(product_id)
        if product:
            self.data_manager.delete_product(product_id)
            self.bot.edit_message_text(
                f"✅ محصول '{product['name']}' حذف شد.",
                user_id,
                call.message.message_id,
                reply_markup=back_button()
            )
        else:
            self.bot.edit_message_text(
                NOT_FOUND_MESSAGE,
                user_id,
                call.message.message_id,
                reply_markup=back_button()
            )
    
    def _handle_delete_sale(self, user_id, call, sale_id):
        """حذف فروش"""
        sale = self.data_manager.get_sale(sale_id)
        if sale:
            if 'product_id' in sale:
                product = self.data_manager.find_product_by_name(sale['product_name'])
                if product:
                    self.data_manager.increase_inventory(product['id'], sale['quantity'])
            
            self.data_manager.delete_sale(sale_id)
            self.bot.edit_message_text(
                f"✅ فروش حذف شد.\n\n📦 موجودی '{sale['product_name']}' بازگردانده شد: +{sale['quantity']} عدد",
                user_id,
                call.message.message_id,
                reply_markup=back_button()
            )
        else:
            self.bot.edit_message_text(
                NOT_FOUND_MESSAGE,
                user_id,
                call.message.message_id,
                reply_markup=back_button()
            )
    
    def _register_cancel_handler(self):
        """لغو عملیات"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "cancel_action")
        def cancel_action(call):
            user_id = call.message.chat.id
            set_user_state(user_id, 'main_menu')
            
            self.bot.edit_message_text(
                CANCEL_MESSAGE,
                user_id,
                call.message.message_id,
                reply_markup=main_menu_keyboard()
            )
