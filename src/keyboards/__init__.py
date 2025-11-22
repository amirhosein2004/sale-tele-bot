# Import from common keyboards
from .common import (
    main_menu_keyboard,
    back_button,
    main_reply_keyboard,
    remove_keyboard,
    quick_actions_keyboard,
    confirmation_keyboard,
    navigation_keyboard,
    help_keyboard,
    share_keyboard
)

# Import from inventory keyboards
from .inventory import (
    inventory_menu_keyboard,
    products_list_keyboard,
    edit_product_keyboard
)

# Import from sales keyboards
from .sales import (
    sales_menu_keyboard,
    sales_list_keyboard,
    edit_sale_keyboard
)

__all__ = [
    # Common
    'main_menu_keyboard',
    'back_button',
    'main_reply_keyboard',
    'remove_keyboard',
    'quick_actions_keyboard',
    'confirmation_keyboard',
    'navigation_keyboard',
    'help_keyboard',
    'share_keyboard',
    
    # Inventory
    'inventory_menu_keyboard',
    'products_list_keyboard',
    'edit_product_keyboard',
    
    # Sales
    'sales_menu_keyboard',
    'sales_list_keyboard',
    'edit_sale_keyboard',
]
