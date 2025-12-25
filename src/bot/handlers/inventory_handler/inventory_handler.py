"""
کلاس مدیریت هندلرهای موجودی محصولات
سازماندهی شده به پنج ماژول:
- menu.py: منوی موجودی
- add_product.py: اضافه کردن محصول
- edit_product.py: ویرایش محصول
- delete_product.py: حذف محصول
- view.py: مشاهده موجودی
"""

from .menu import InventoryMenu
from .add_product import AddProduct
from .edit_product import EditProduct
from .delete_product import DeleteProduct
from .view import ViewInventory


class InventoryHandler:
    """کلاس مدیریت هندلرهای موجودی - مختصر و منسق"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        
        # ایجاد نمونه‌های ماژول‌ها
        self.menu = InventoryMenu(bot, data_manager)
        self.add_product = AddProduct(bot, data_manager)
        self.edit_product = EditProduct(bot, data_manager)
        self.delete_product = DeleteProduct(bot, data_manager)
        self.view = ViewInventory(bot, data_manager)
    
    def register(self):
        """ثبت تمام هندلرهای موجودی از طریق ماژول‌ها"""
        self.menu.register()
        self.add_product.register()
        self.edit_product.register()
        self.delete_product.register()
        self.view.register()
