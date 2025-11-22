# Import and register all handlers
from .state import (
    data_manager,
    get_user_state,
    set_user_state,
    get_user_data,
    clear_user_data,
    is_user_processing,
    set_user_processing
)
from .common import (
    register_common_handlers,
    register_text_message_handlers
)
from .inventory import register_inventory_handlers
from .sales import register_sales_handlers


def register_handlers(bot):
    """ثبت تمام هندلرها"""
    register_common_handlers(bot)
    register_inventory_handlers(bot, data_manager)
    register_sales_handlers(bot, data_manager)
    register_text_message_handlers(bot)


__all__ = [
    'register_handlers',
    'data_manager',
    'get_user_state',
    'set_user_state',
    'get_user_data',
    'clear_user_data',
    'is_user_processing',
    'set_user_processing',
]
