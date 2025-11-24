"""
کلاس مدیریت هندلرهای موجودی محصولات
سازماندهی شده به چهار ماژول:
- menu.py: منوی موجودی
- add_product.py: اضافه کردن محصول
- edit_delete.py: ویرایش و حذف محصول
- view.py: مشاهده موجودی
"""

from .menu import InventoryMenu
from .add_product import AddProduct
from .edit_delete import EditDelete
from .view import ViewInventory


class InventoryHandler:
    """کلاس مدیریت هندلرهای موجودی - مختصر و منسق"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        
        # ایجاد نمونه‌های ماژول‌ها
        self.menu = InventoryMenu(bot, data_manager)
        self.add_product = AddProduct(bot, data_manager)
        self.edit_delete = EditDelete(bot, data_manager)
        self.view = ViewInventory(bot, data_manager)
    
    def register(self):
        """ثبت تمام هندلرهای موجودی از طریق ماژول‌ها"""
        self.menu.register()
        self.add_product.register()
        self.edit_delete.register()
        self.view.register()
