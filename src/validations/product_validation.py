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
            دیکشنری شامل: is_valid (bool), error_message (str|None), name (str|None)
        """
        if not name or not name.strip():
            return {
                'is_valid': False,
                'error_message': '❌ نام نمی‌تواند خالی باشد.'
            }
        
        name_str = name.strip()
        
        # بررسی طول نام (حداقل 2، حداکثر 155 کاراکتر)
        if len(name_str) < 2:
            return {
                'is_valid': False,
                'error_message': '❌ نام باید حداقل 2 کاراکتر باشد.'
            }
        
        if len(name_str) > 155:
            return {
                'is_valid': False,
                'error_message': '❌ نام نمی‌تواند بیش از 155 کاراکتر باشد.'
            }
        
        return {
            'is_valid': True,
            'error_message': None,
            'name': name_str
        }
    
    def validate_product_quantity(self, quantity: int) -> dict: # ✅ 
        """
        ولیدیشن موجودی محصول
        
        Args:
            quantity: موجودی
            
        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None), quantity (int|None)
        """
        try:
            qty = int(quantity)
            if qty < 0:
                raise ValueError("موجودی نمی‌تواند منفی باشد")
            
            # بررسی حد معقول (حداکثر 1 میلیون)
            if qty > 1_000_000:
                raise ValueError("موجودی بیش از حد است")
                
        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error_message': '❌ لطفاً عدد صحیح و مثبت وارد کنید.'
            }
        
        return {
            'is_valid': True,
            'error_message': None,
            'quantity': qty
        }
