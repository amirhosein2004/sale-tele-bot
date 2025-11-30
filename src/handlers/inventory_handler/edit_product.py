"""
هندلرهای ویرایش محصول
"""

from ...keyboards import (
    edit_product_keyboard,
    back_button,
    cancel_button,
    products_list_keyboard_with_pagination,
)
from ...states.state import (
    get_user_state,
    set_user_state,
    get_user_data,
    is_user_processing,
    set_user_processing
)
from ...services.inventory_services import InventoryService


class EditProduct:
    """مدیریت ویرایش محصول"""
    
    ITEMS_PER_PAGE = 20
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.inventory_service = InventoryService(data_manager)
    
    def register(self):
        """ثبت هندلرهای ویرایش محصول"""
        self._register_edit_product_handlers()
        self._register_pagination_handler()
    
    def _register_edit_product_handlers(self):
        """هندلرهای ویرایش محصول"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "edit_product_list")
        def edit_product_list(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                # دریافت صفحه اول از سرویس
                page_data = self.inventory_service.get_products_for_edit_page(page=1, items_per_page=self.ITEMS_PER_PAGE)
                
                if not page_data['has_products']:
                    self.bot.send_message(user_id, page_data['text'], reply_markup=back_button("inventory"))
                    return
                
                set_user_state(user_id, 'edit_product')
                
                # ساخت کیبورد با صفحه‌بندی
                keyboard = products_list_keyboard_with_pagination(
                    page_data['products'],
                    page_data['page'],
                    page_data['total_pages'],
                    for_sale=False
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
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("select_product_") and get_user_state(call.message.chat.id) == 'edit_product')
        def select_product(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                product_id = int(call.data.split("_")[2])
                product = self.data_manager.get_product(product_id)
                
                if not product:
                    self.bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button("inventory"))
                    return
                
                get_user_data(user_id)['selected_product_id'] = product_id
                
                text = f"📦 محصول: {product['name']}\n"
                text += f"📊 موجودی: {product['quantity']} عدد\n\n"
                text += "چه کاری می‌خواهید انجام دهید؟"
                
                self.bot.edit_message_text(
                    text,
                    user_id,
                    call.message.message_id,
                    reply_markup=edit_product_keyboard(product_id)
                )
            finally:
                set_user_processing(user_id, False)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("edit_name_"))
        def edit_name_start(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                product_id = int(call.data.split("_")[2])
                
                # استفاده از ولیدیتور برای بررسی وجود محصول
                validation = self.inventory_service.product_validator.validate_product_exists(product_id)
                
                if not validation['is_valid']:
                    self.bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button("inventory"))
                    return
                
                product = validation['product']
                get_user_data(user_id)['selected_product_id'] = product_id
                set_user_state(user_id, 'edit_product_name')
                
                msg = self.bot.send_message(user_id, f"📝 نام جدید را وارد کنید (فعلی: {product['name']}):", reply_markup=cancel_button())
                self.bot.register_next_step_handler(msg, self._process_edit_name)
            finally:
                set_user_processing(user_id, False)
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("edit_qty_"))
        def edit_quantity_start(call):
            user_id = call.message.chat.id
            
            if is_user_processing(user_id):
                self.bot.answer_callback_query(call.id, "⏳ لطفاً صبر کنید...", show_alert=False)
                return
            
            set_user_processing(user_id, True)
            try:
                product_id = int(call.data.split("_")[2])
                
                # استفاده از ولیدیتور برای بررسی وجود محصول
                validation = self.inventory_service.product_validator.validate_product_exists(product_id)
                
                if not validation['is_valid']:
                    self.bot.send_message(user_id, "❌ محصول یافت نشد.", reply_markup=back_button("inventory"))
                    return
                
                product = validation['product']
                get_user_data(user_id)['selected_product_id'] = product_id
                set_user_state(user_id, 'edit_product_qty')
                
                msg = self.bot.send_message(user_id, f"📝 موجودی جدید را وارد کنید (فعلی: {product['quantity']}):", reply_markup=cancel_button())
                self.bot.register_next_step_handler(msg, self._process_edit_quantity)
            finally:
                set_user_processing(user_id, False)
    
    def _process_edit_name(self, message):
        """پردازش ویرایش نام محصول"""
        user_id = message.chat.id
        new_name = message.text
        product_id = get_user_data(user_id).get('selected_product_id')
        
        # استفاده از سرویس برای بروزرسانی (سرویس انجام ولیدیشن می‌دهد)
        result = self.inventory_service.update_product_name(product_id, new_name)
        
        if not result['success']:
            msg = self.bot.send_message(user_id, f"{result['error_message']} دوباره تلاش کنید:", reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_edit_name)
            return
        
        self.bot.send_message(
            user_id,
            f"✅ نام محصول از '{result['old_name']}' به '{result['new_name']}' تغییر یافت.",
            reply_markup=back_button("inventory")
        )
        
        set_user_state(user_id, 'inventory_menu')
    
    def _process_edit_quantity(self, message):
        """پردازش ویرایش موجودی"""
        user_id = message.chat.id
        product_id = get_user_data(user_id).get('selected_product_id')
        new_quantity = message.text
        
        # استفاده از سرویس برای بروزرسانی (سرویس انجام ولیدیشن می‌دهد)
        result = self.inventory_service.update_product_quantity(product_id, new_quantity)
        
        if not result['success']:
            msg = self.bot.send_message(user_id, f"{result['error_message']} دوباره تلاش کنید:", reply_markup=cancel_button())
            self.bot.register_next_step_handler(msg, self._process_edit_quantity)
            return
        
        self.bot.send_message(
            user_id,
            f"✅ موجودی '{result['product']['name']}' به {result['new_quantity']} عدد تغییر یافت.",
            reply_markup=back_button("inventory")
        )
        
        set_user_state(user_id, 'inventory_menu')
    
    def _register_pagination_handler(self):
        """هندلر صفحه‌بندی محصولات برای ویرایش"""
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("edit_products_page_"))
        def handle_edit_products_pagination(call):
            user_id = call.message.chat.id
            message_id = call.message.message_id
            page = int(call.data.split("_")[-1])
            
            # دریافت صفحه از سرویس
            page_data = self.inventory_service.get_products_for_edit_page(page=page, items_per_page=self.ITEMS_PER_PAGE)
            
            # ساخت کیبورد
            keyboard = products_list_keyboard_with_pagination(
                page_data['products'],
                page_data['page'],
                page_data['total_pages'],
                for_sale=False
            )
            
            self.bot.edit_message_text(
                page_data['text'],
                user_id,
                message_id,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
