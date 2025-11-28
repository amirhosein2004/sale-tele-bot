"""
ولیدیشن‌های حذف محصول و فروش
"""


class DeletionValidator:
    """ولیدیشن عملیات حذف"""
    
    def __init__(self, data_manager):
        """
        Args:
            data_manager: مدیریت‌کننده داده‌ها
        """
        self.data_manager = data_manager
    
    def validate_product_deletion(self, product_id: int) -> dict: # ✅ 
        """
        ولیدیشن حذف محصول
        
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
    
    def validate_sale_deletion(self, sale_id: int) -> dict: # ✅ 
        """
        ولیدیشن حذف فروش
        
        Args:
            sale_id: شناسه فروش
            
        Returns:
            دیکشنری شامل: is_valid (bool), sale (dict|None)
        """
        sale = self.data_manager.get_sale(sale_id)
        
        return {
            'is_valid': sale is not None,
            'sale': sale
        }
