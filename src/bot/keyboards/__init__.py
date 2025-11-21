# Import from common keyboards
from .common import (
    main_menu_keyboard,
    back_button,
    main_reply_keyboard,
    # remove_keyboard,
    quick_actions_keyboard,
    confirmation_keyboard,
    help_keyboard,
    share_keyboard,
    cancel_button
)

# Import from inventory keyboards
from .inventory import (
    inventory_menu_keyboard,
    edit_product_keyboard,
    products_list_keyboard_with_pagination
)

# Import from sales keyboards
from .sales import (
    sales_menu_keyboard,
    edit_sale_keyboard,
    sales_list_keyboard_with_pagination
)

# Import from pagination keyboards
from .pagination import (
    pagination_keyboard
)

__all__ = [
    # Common
    'main_menu_keyboard',
    'back_button',
    'main_reply_keyboard',
    # 'remove_keyboard',
    'quick_actions_keyboard',
    'confirmation_keyboard',
    'help_keyboard',
    'share_keyboard',
    'cancel_button',
    
    # Inventory
    'inventory_menu_keyboard',
    'edit_product_keyboard',
    'products_list_keyboard_with_pagination',
    
    # Sales
    'sales_menu_keyboard',
    'edit_sale_keyboard',
    'sales_list_keyboard_with_pagination',

    # Pagination
    "pagination_keyboard",
]
