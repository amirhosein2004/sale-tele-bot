"""
کلاس مدیریت هندلرهای مشترک
سازماندهی شده به سه ماژول:
- common.py: دستورات اساسی
- confirmation.py: منطق تایید و حذف
- navigation.py: ناوبری و منوهای سریع
"""

from .common import CommonCommands
from .confirmation import ConfirmationManager
from .navigation import NavigationMenu


class CommonHandler:
    """کلاس مدیریت هندلرهای مشترک - مختصر و منسق"""
    
    def __init__(self, bot, data_manager):
        self.bot = bot
        self.data_manager = data_manager
        
        # ایجاد نمونه‌های ماژول‌ها
        self.common_commands = CommonCommands(bot, data_manager)
        self.confirmation = ConfirmationManager(bot, data_manager)
        self.navigation = NavigationMenu(bot, data_manager)
    
    def register(self):
        """ثبت تمام هندلرهای مشترک از طریق ماژول‌ها"""
        self.common_commands.register()
        self.confirmation.register()
        self.navigation.register()
