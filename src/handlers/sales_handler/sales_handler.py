"""
کلاس مدیریت هندلرهای فروش
سازماندهی شده به چهار ماژول:
- menu.py: منوی فروش
- add_sale.py: اضافه کردن فروش
- view_sales.py: مشاهده و حذف فروش
- edit_sale.py: ویرایش فروش
"""

from .menu import SalesMenu
from .add_sale import AddSale
from .view_sales import ViewSales
from .edit_sale import EditSale


class SalesHandler:
    """کلاس مدیریت هندلرهای فروش - مختصر و منسق"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        
        # ایجاد نمونه‌های ماژول‌ها
        self.menu = SalesMenu(bot, data_manager)
        self.add_sale = AddSale(bot, data_manager)
        self.view_sales = ViewSales(bot, data_manager)
        self.edit_sale = EditSale(bot, data_manager)
    
    def register(self):
        """ثبت تمام هندلرهای فروش از طریق ماژول‌ها"""
        self.menu.register()
        self.add_sale.register()
        self.view_sales.register()
        self.edit_sale.register()
