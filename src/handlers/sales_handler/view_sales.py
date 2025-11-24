"""
هندلرهای مشاهده و حذف فروش
"""

from ...keyboards import sales_list_keyboard, edit_sale_keyboard, back_button, confirmation_keyboard
from ..state import (
    set_user_state,
    get_user_data,
    is_user_processing,
    set_user_processing
)


class ViewSales:
    """مدیریت مشاهده و حذف فروش"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
    
    def register(self):
        """ثبت هندلرهای مشاهده و حذف فروش"""
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
                sales = self.data_manager.get_all_sales()
                
                if not sales:
                    self.bot.send_message(user_id, "📊 هیچ فروشی ثبت نشده است.", reply_markup=back_button())
                    return
                
                set_user_state(user_id, 'view_sales')
                self.bot.edit_message_text(
                    "📊 لیست فروش‌ها\n\nفروش مورد نظر را انتخاب کنید:",
                    user_id,
                    call.message.message_id,
                    reply_markup=sales_list_keyboard(sales)
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
                sale = self.data_manager.get_sale(sale_id)
                
                if not sale:
                    self.bot.send_message(user_id, "❌ فروش یافت نشد.", reply_markup=back_button())
                    return
                
                get_user_data(user_id)['selected_sale_id'] = sale_id
                
                text = f"🧾 فروش شماره {sale['id']}\n"
                text += f"📦 محصول: {sale['product_name']}\n"
                text += f"🔢 تعداد: {sale['quantity']}\n"
                text += f"💵 قیمت واحد: {sale['sale_price']}\n"
                text += f"💰 کل فروش: {sale['total_sale_price']}\n"
                text += f"💸 کل خرید: {sale['total_cost']}\n"
                text += f"🏷️ هزینه‌های جانبی: {sale['extra_cost']}\n"
                text += f"📈 سود خالص: {sale['net_profit']}\n"
                text += f"📅 تاریخ: {sale['date']}\n\n"
                text += "چه کاری می‌خواهید انجام دهید؟"
                
                self.bot.send_message(user_id, text, reply_markup=edit_sale_keyboard(sale_id))
            finally:
                set_user_processing(user_id, False)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("delete_sale_"))
        def delete_sale(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                sale_id = int(call.data.split("_")[2])
                sale = self.data_manager.get_sale(sale_id)
                
                if sale:
                    self.bot.edit_message_text(
                        f"⚠️ آیا مطمئن هستید که می‌خواهید فروش '{sale['product_name']}' را حذف کنید؟\n\nاین عمل قابل بازگشت نیست!",
                        user_id,
                        call.message.message_id,
                        reply_markup=confirmation_keyboard("delete_sale", sale_id)
                    )
                else:
                    self.bot.send_message(user_id, "❌ فروش یافت نشد.", reply_markup=back_button())
            finally:
                set_user_processing(user_id, False)
