# Import and register all handlers
from ..states.state import (
    data_manager,
)
from .common_handler import CommonHandler
from .inventory_handler import InventoryHandler
from .sales_handler import SalesHandler


def register_handlers(bot):
    """ثبت تمام هندلرها"""
    common_handler = CommonHandler(bot, data_manager)
    common_handler.register()
    
    inventory_handler = InventoryHandler(bot, data_manager)
    inventory_handler.register()
    
    sales_handler = SalesHandler(bot, data_manager)
    sales_handler.register()
