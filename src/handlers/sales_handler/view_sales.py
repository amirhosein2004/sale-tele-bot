"""
هندلرهای مشاهده فروش
"""

from ...keyboards import sales_list_keyboard, edit_sale_keyboard, back_button
from ..state import (
    set_user_state,
    get_user_data,
    is_user_processing,
    set_user_processing
)
from ...services.sale_services import SalesService


class ViewSales:
    """مدیریت مشاهده فروش"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.sales_service = SalesService(data_manager)
    
    def register(self):
        """ثبت هندلرهای مشاهده فروش"""
        self._register_view_sales_handlers()
    
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
                # استفاده از سرویس برای دریافت لیست فروش‌ها
                result = self.sales_service.get_sales_list_for_display()
                
                if not result['has_sales']:
                    self.bot.send_message(user_id, result['message'], reply_markup=back_button())
                    return
                
                set_user_state(user_id, 'view_sales')
                self.bot.edit_message_text(
                    "📊 لیست فروش‌ها\n\nفروش مورد نظر را انتخاب کنید:",
                    user_id,
                    call.message.message_id,
                    reply_markup=sales_list_keyboard(result['sales'])
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
                    self.bot.send_message(user_id, result['text'], reply_markup=back_button())
                    return
                
                get_user_data(user_id)['selected_sale_id'] = sale_id
                
                self.bot.send_message(user_id, result['text'], reply_markup=edit_sale_keyboard(sale_id))
            finally:
                set_user_processing(user_id, False)
