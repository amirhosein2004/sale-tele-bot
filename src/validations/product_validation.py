"""
ولیدیشن‌های محصول
"""


class ProductValidator:
    """ولیدیشن عملیات محصول"""
    
    def __init__(self, data_manager):
        """
        Args:
            data_manager: مدیریت‌کننده داده‌ها
        """
        self.data_manager = data_manager
    
    def validate_product_exists(self, product_id: int) -> dict: # ✅ 
        """
        ولیدیشن وجود محصول
        
        Args:
            product_id: شناسه محصول
            
        Returns:
            دیکشنری شامل: is_valid (bool), product (dict|None)
        """
        product = self.data_manager.get_product(product_id)
        
        return {
            'is_valid': product is not None,
            'product': product
        }
    
    def validate_product_name(self, name: str) -> dict: # ✅ 
        """
        ولیدیشن نام محصول
        
        Args:
            name: نام محصول
            
        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None)
        """
        if not name or not name.strip():
            return {
                'is_valid': False,
                'error_message': '❌ نام نمی‌تواند خالی باشد.'
            }
        
        return {
            'is_valid': True,
            'error_message': None
        }
    
    def validate_product_quantity(self, quantity: int) -> dict: # ✅ 
        """
        ولیدیشن موجودی محصول
        
        Args:
            quantity: موجودی
            
        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None)
        """
        try:
            qty = int(quantity)
            if qty < 0:
                raise ValueError
        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error_message': '❌ لطفاً عدد صحیح و مثبت وارد کنید.'
            }
        
        return {
            'is_valid': True,
            'error_message': None
        }
