"""
ماژول دستورات اساسی
شامل: start, help, back, share
"""

from ...keyboards import (
    main_menu_keyboard,
    back_button,
    main_reply_keyboard,
    help_keyboard,
    share_keyboard,
    inventory_menu_keyboard,
    sales_menu_keyboard,
    quick_actions_keyboard
)
from ..state import (
    set_user_state,
    clear_user_data,
    is_user_processing
)
from ...utils import (
    HELP_TEXT,
    START_MESSAGE,
    START_SUBMENU,
    REPORT_SHARED_MESSAGE,
    QUICK_ACTIONS_TITLE,
    SHARE_MENU_TITLE
)


class CommonCommands:
    """مدیریت دستورات اساسی"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
    def register(self):
        """ثبت تمام دستورات اساسی"""
        self._register_start_handler()
        self._register_back_to_main_handler()
        self._register_help_handler()
        self._register_share_report_handler()
        self._register_text_message_handler()
    
    def _register_start_handler(self):
        """هندلر دستور شروع"""
        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            user_id = message.chat.id
            set_user_state(user_id, 'main_menu')
            clear_user_data(user_id)
            
            self.bot.send_message(
                user_id,
                START_MESSAGE,
                reply_markup=main_menu_keyboard()
            )
            
            self.bot.send_message(
                user_id,
                START_SUBMENU,
                reply_markup=main_reply_keyboard()
            )
    
    def _register_back_to_main_handler(self):
        """بازگشت به منوی اصلی"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
        def back_to_main(call):
            user_id = call.message.chat.id
            set_user_state(user_id, 'main_menu')
            clear_user_data(user_id)
            
            self.bot.edit_message_text(
                START_MESSAGE,
                user_id,
                call.message.message_id,
                reply_markup=main_menu_keyboard()
            )
    
    def _register_help_handler(self):
        """نمایش راهنما"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "show_help")
        def show_help(call):
            user_id = call.message.chat.id
            
            self.bot.edit_message_text(
                HELP_TEXT,
                user_id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=back_button()
            )
    
    def _register_share_report_handler(self):
        """اشتراک‌گذاری گزارش"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "share_report")
        def share_report(call):
            user_id = call.message.chat.id
            
            inventory_text = self.data_manager.get_products_text()
            sales_summary = self.data_manager.get_sales_summary()
            
            report_text = f"📊 *گزارش کامل فروشگاه*\n\n{inventory_text}\n\n{sales_summary}"
            
            self.bot.send_message(
                user_id,
                report_text,
                parse_mode="Markdown"
            )
            
            self.bot.answer_callback_query(call.id, REPORT_SHARED_MESSAGE)
    
    def _register_text_message_handler(self):
        """هندلر پیام‌های متنی"""
        @self.bot.message_handler(func=lambda message: True)
        def handle_text_messages(message):
            user_id = message.chat.id
            text = message.text.strip()
            
            if is_user_processing(user_id):
                return
            
            if text == "📦 موجودی محصولات":
                set_user_state(user_id, 'inventory_menu')
                self.bot.send_message(
                    user_id,
                    "📦 منوی موجودی محصولات",
                    reply_markup=inventory_menu_keyboard()
                )
            elif text == "💳 ثبت فروش":
                set_user_state(user_id, 'sales_menu')
                self.bot.send_message(
                    user_id,
                    "💳 منوی فروش محصولات",
                    reply_markup=sales_menu_keyboard()
                )
            elif text == "📊 گزارش‌ها":
                inventory_text = self.data_manager.get_products_text()
                sales_summary = self.data_manager.get_sales_summary()
                
                report_text = f"📊 *گزارش کلی*\n\n{inventory_text}\n\n{sales_summary}"
                self.bot.send_message(
                    user_id,
                    report_text,
                    parse_mode="Markdown",
                    reply_markup=main_menu_keyboard()
                )
            elif text == "🔧 عملیات سریع":
                self.bot.send_message(
                    user_id,
                    QUICK_ACTIONS_TITLE,
                    reply_markup=quick_actions_keyboard()
                )
            elif text == "📖 راهنما":
                self.bot.send_message(
                    user_id,
                    HELP_TEXT,
                    parse_mode="Markdown",
                    reply_markup=help_keyboard()
                )
            elif text == "📤 اشتراک‌گذاری":
                self.bot.send_message(
                    user_id,
                    SHARE_MENU_TITLE,
                    reply_markup=share_keyboard()
                )
            else:
                set_user_state(user_id, 'main_menu')
                clear_user_data(user_id)
                
                self.bot.send_message(
                    user_id,
                    START_MESSAGE,
                    reply_markup=main_menu_keyboard()
                )
