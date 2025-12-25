"""
هندلر مشاهده موجودی محصولات
"""

from ...keyboards import back_button
from ...keyboards.pagination import pagination_keyboard
from ....services.inventory_services import InventoryService


class ViewInventory:
    """مدیریت مشاهده موجودی"""
    
    ITEMS_PER_PAGE = 20
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        self.inventory_service = InventoryService(data_manager)
    
    def register(self):
        """ثبت هندلرهای مشاهده موجودی"""
        self._register_view_inventory_handler()
        self._register_pagination_handler()

    def _register_view_inventory_handler(self):
        """هندلر مشاهده لیست محصولات"""
        @self.bot.callback_query_handler(func=lambda call: call.data == "view_inventory")
        def view_inventory(call):
            user_id = call.message.chat.id
            message_id = call.message.message_id
            
            # دریافت صفحه اول از سرویس
            page_data = self.inventory_service.get_inventory_page(page=1, items_per_page=self.ITEMS_PER_PAGE)
            
            # ساخت کیبورد
            keyboard = pagination_keyboard("products_page", page_data['page'], page_data['total_pages'])
            keyboard.add(back_button("inventory").keyboard[0][0])
            
            self.bot.edit_message_text(
                page_data['text'],
                user_id,
                message_id,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    
    def _register_pagination_handler(self):
        """هندلر صفحه‌بندی"""
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("products_page_"))
        def handle_pagination(call):
            user_id = call.message.chat.id
            message_id = call.message.message_id
            page = int(call.data.split("_")[-1])
            
            # دریافت صفحه از سرویس
            page_data = self.inventory_service.get_inventory_page(page=page, items_per_page=self.ITEMS_PER_PAGE)
            
            # ساخت کیبورد
            keyboard = pagination_keyboard("products_page", page_data['page'], page_data['total_pages'])
            keyboard.add(back_button("inventory").keyboard[0][0])
            
            self.bot.edit_message_text(
                page_data['text'],
                user_id,
                message_id,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
