# هندلرهای مشترک
from ..keyboards import (
    main_menu_keyboard,
    back_button,
    main_reply_keyboard,
    quick_actions_keyboard,
    help_keyboard,
    share_keyboard,
    inventory_menu_keyboard,
    sales_menu_keyboard
)
from .state import (
    data_manager,
    set_user_state,
    clear_user_data,
    is_user_processing,
    set_user_processing
)
from ..utils import (
    HELP_TEXT,
    START_MESSAGE,
    START_SUBMENU,
    CANCEL_MESSAGE,
    PROCESSING_MESSAGE,
    ERROR_MESSAGE,
    NOT_FOUND_MESSAGE,
    QUICK_ACTIONS_TITLE,
    SHARE_MENU_TITLE,
    DISABLED_BUTTON_MESSAGE,
    PAGINATION_PREV_MESSAGE,
    PAGINATION_NEXT_MESSAGE,
    REPORT_SHARED_MESSAGE
)


def register_common_handlers(bot):
    """ثبت هندلرهای مشترک"""
    
    @bot.message_handler(commands=['start'])
    def start_handler(message):
        """هندلر دستور شروع"""
        user_id = message.chat.id
        set_user_state(user_id, 'main_menu')
        clear_user_data(user_id)
        
        bot.send_message(
            user_id,
            START_MESSAGE,
            reply_markup=main_menu_keyboard()
        )
        
        # ارسال صفحه‌کلید کشویی
        bot.send_message(
            user_id,
            START_SUBMENU,
            reply_markup=main_reply_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
    def back_to_main(call):
        """بازگشت به منوی اصلی"""
        user_id = call.message.chat.id
        set_user_state(user_id, 'main_menu')
        clear_user_data(user_id)
        
        bot.edit_message_text(
            START_MESSAGE,
            user_id,
            call.message.message_id,
            reply_markup=main_menu_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "show_help")
    def show_help(call):
        """نمایش راهنما"""
        user_id = call.message.chat.id
        
        bot.edit_message_text(
            HELP_TEXT,
            user_id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=back_button()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "share_report")
    def share_report(call):
        """اشتراک‌گذاری گزارش"""
        user_id = call.message.chat.id
        
        # تولید گزارش کامل
        inventory_text = data_manager.get_products_text()
        sales_summary = data_manager.get_sales_summary()
        
        report_text = f"📊 *گزارش کامل فروشگاه*\n\n{inventory_text}\n\n{sales_summary}"
        
        bot.send_message(
            user_id,
            report_text,
            parse_mode="Markdown"
        )
        
        bot.answer_callback_query(call.id, REPORT_SHARED_MESSAGE)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
    def handle_confirmation(call):
        """مدیریت تأییدیه‌ها"""
        user_id = call.message.chat.id
        
        if is_user_processing(user_id):
            bot.answer_callback_query(call.id, PROCESSING_MESSAGE, show_alert=False)
            return
        
        set_user_processing(user_id, True)
        try:
            parts = call.data.split("_")
            if len(parts) < 4:
                bot.answer_callback_query(call.id, ERROR_MESSAGE, show_alert=True)
                return
            
            # فرمت: confirm_delete_product_123 یا confirm_delete_sale_456
            action_type = parts[1]  # "delete"
            item_type = parts[2]    # "product" یا "sale"
            action = f"{action_type}_{item_type}"  # "delete_product" یا "delete_sale"
            
            try:
                item_id = int(parts[3])
            except ValueError:
                bot.answer_callback_query(call.id, ERROR_MESSAGE, show_alert=True)
                return
            
            if action == "delete_product":
                product = data_manager.get_product(item_id)
                if product:
                    data_manager.delete_product(item_id)
                    bot.edit_message_text(
                        f"✅ محصول '{product['name']}' حذف شد.",
                        user_id,
                        call.message.message_id,
                        reply_markup=back_button()
                    )
                else:
                    bot.edit_message_text(
                        NOT_FOUND_MESSAGE,
                        user_id,
                        call.message.message_id,
                        reply_markup=back_button()
                    )
            
            elif action == "delete_sale":
                sale = data_manager.get_sale(item_id)
                if sale:
                    # بازگرداندن موجودی
                    if 'product_id' in sale:
                        product = data_manager.find_product_by_name(sale['product_name'])
                        if product:
                            data_manager.increase_inventory(product['id'], sale['quantity'])
                    
                    # حذف فروش
                    data_manager.delete_sale(item_id)
                    bot.edit_message_text(
                        f"✅ فروش حذف شد.\n\n📦 موجودی '{sale['product_name']}' بازگردانده شد: +{sale['quantity']} عدد",
                        user_id,
                        call.message.message_id,
                        reply_markup=back_button()
                    )
                else:
                    bot.edit_message_text(
                        NOT_FOUND_MESSAGE,
                        user_id,
                        call.message.message_id,
                        reply_markup=back_button()
                    )
            
            set_user_state(user_id, 'main_menu')
        finally:
            set_user_processing(user_id, False)
    
    @bot.callback_query_handler(func=lambda call: call.data == "cancel_action")
    def cancel_action(call):
        """لغو عملیات"""
        user_id = call.message.chat.id
        set_user_state(user_id, 'main_menu')
        
        bot.edit_message_text(
            CANCEL_MESSAGE,
            user_id,
            call.message.message_id,
            reply_markup=main_menu_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data in ["prev_page", "next_page"])
    def handle_pagination(call):
        """مدیریت صفحه‌بندی"""
        user_id = call.message.chat.id
        
        # در حال حاضر فقط پیام اطلاع‌رسانی
        if call.data == "prev_page":
            bot.answer_callback_query(call.id, PAGINATION_PREV_MESSAGE, show_alert=False)
        else:
            bot.answer_callback_query(call.id, PAGINATION_NEXT_MESSAGE, show_alert=False)
    
    @bot.callback_query_handler(func=lambda call: call.data == "quick_actions")
    def quick_actions_menu(call):
        """منوی عملیات سریع"""
        user_id = call.message.chat.id
        
        bot.edit_message_text(
            QUICK_ACTIONS_TITLE,
            user_id,
            call.message.message_id,
            reply_markup=quick_actions_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "share_menu")
    def share_menu(call):
        """منوی اشتراک‌گذاری"""
        user_id = call.message.chat.id
        
        bot.edit_message_text(
            SHARE_MENU_TITLE,
            user_id,
            call.message.message_id,
            reply_markup=share_keyboard()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == "disabled")
    def disabled_button(call):
        """مدیریت دکمه‌های غیرفعال"""
        bot.answer_callback_query(
            call.id, 
            DISABLED_BUTTON_MESSAGE, 
            show_alert=True
        )


def register_text_message_handlers(bot):
    """ثبت هندلرهای پیام‌های متنی"""
    
    @bot.message_handler(func=lambda message: True)
    def handle_text_messages(message):
        """هندلر پیام‌های متنی"""
        user_id = message.chat.id
        text = message.text.strip()
        
        # اگر کاربر در حال پردازش است، نادیده بگیر
        if is_user_processing(user_id):
            return
        
        # بررسی پیام‌های صفحه‌کلید کشویی
        if text == "📦 موجودی محصولات":
            set_user_state(user_id, 'inventory_menu')
            bot.send_message(
                user_id,
                "📦 منوی موجودی محصولات",
                reply_markup=inventory_menu_keyboard()
            )
        elif text == "💳 ثبت فروش":
            set_user_state(user_id, 'sales_menu')
            bot.send_message(
                user_id,
                "💳 منوی فروش محصولات",
                reply_markup=sales_menu_keyboard()
            )
        elif text == "📊 گزارش‌ها":
            # نمایش گزارش کلی
            inventory_text = data_manager.get_products_text()
            sales_summary = data_manager.get_sales_summary()
            
            report_text = f"📊 *گزارش کلی*\n\n{inventory_text}\n\n{sales_summary}"
            bot.send_message(
                user_id,
                report_text,
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard()
            )
        elif text == "🔧 عملیات سریع":
            bot.send_message(
                user_id,
                QUICK_ACTIONS_TITLE,
                reply_markup=quick_actions_keyboard()
            )
        elif text == "📖 راهنما":
            bot.send_message(
                user_id,
                HELP_TEXT,
                parse_mode="Markdown",
                reply_markup=help_keyboard()
            )
        elif text == "📤 اشتراک‌گذاری":
            bot.send_message(
                user_id,
                SHARE_MENU_TITLE,
                reply_markup=share_keyboard()
            )
        else:
            # برای هر پیام دیگر، منو را نشان بده
            set_user_state(user_id, 'main_menu')
            clear_user_data(user_id)
            
            bot.send_message(
                user_id,
                START_MESSAGE,
                reply_markup=main_menu_keyboard()
            )
