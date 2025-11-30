"""
هندلرهای مشاهده فروش
"""

from ...keyboards import (
    edit_sale_keyboard,
    back_button,
    sales_list_keyboard_with_pagination,
)
from ...states.state import (
    set_user_state,
    get_user_data,
    is_user_processing,
    set_user_processing
)
from ...services.sale_services import SalesService


class ViewSales:
    """مدیریت مشاهده فروش"""
    
    ITEMS_PER_PAGE = 20
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.sales_service = SalesService(data_manager)
    
    def register(self):
        """ثبت هندلرهای مشاهده فروش"""
        self._register_view_sales_handlers()
        self._register_pagination_handler()
    
    def _register_view_sales_handlers(self):
        """هندلرهای مشاهده فروش‌ها"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "view_sales_list")
        def view_sales_list(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                # دریافت صفحه اول از سرویس
                page_data = self.sales_service.get_sales_page(page=1, items_per_page=self.ITEMS_PER_PAGE)
                
                if not page_data['has_sales']:
                    self.bot.send_message(user_id, page_data['message'], reply_markup=back_button("sales"))
                    return
                
                set_user_state(user_id, 'view_sales')
                
                # ساخت کیبورد با صفحه‌بندی
                keyboard = sales_list_keyboard_with_pagination(
                    page_data['sales'],
                    page_data['page'],
                    page_data['total_pages']
                )
                
                self.bot.edit_message_text(
                    page_data['text'],
                    user_id,
                    call.message.message_id,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            finally:
                set_user_processing(user_id, False)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("select_sale_"))
        def select_sale(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                sale_id = int(call.data.split("_")[2])
                
                # استفاده از سرویس برای دریافت جزئیات فروش
                result = self.sales_service.get_sale_details(sale_id)
                
                if not result['success']:
                    self.bot.send_message(user_id, result['text'], reply_markup=back_button("sales"))
                    return
                
                get_user_data(user_id)['selected_sale_id'] = sale_id
                
                self.bot.send_message(user_id, result['text'], reply_markup=edit_sale_keyboard(sale_id))
            finally:
                set_user_processing(user_id, False)
    
    def _register_pagination_handler(self):
        """هندلر صفحه‌بندی فروش‌ها"""
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("sales_page_"))
        def handle_sales_pagination(call):
            user_id = call.message.chat.id
            message_id = call.message.message_id
            page = int(call.data.split("_")[-1])
            
            # دریافت صفحه از سرویس
            page_data = self.sales_service.get_sales_page(page=page, items_per_page=self.ITEMS_PER_PAGE)
            
            # ساخت کیبورد
            keyboard = sales_list_keyboard_with_pagination(
                page_data['sales'],
                page_data['page'],
                page_data['total_pages']
            )
            
            self.bot.edit_message_text(
                page_data['text'],
                user_id,
                message_id,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
