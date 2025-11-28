"""
سرویس مدیریت موجودی و محصولات
"""

from ...validations.deletion_validation import DeletionValidator
from ...validations.product_validation import ProductValidator


class InventoryService:
    """سرویس عملیات موجودی"""
    
    def __init__(self, data_manager):
        """
        Args:
            data_manager: مدیریت‌کننده داده‌ها
        """
        self.data_manager = data_manager
        self.deletion_validator = DeletionValidator(data_manager)
        self.product_validator = ProductValidator(data_manager)
    
    def format_products_list(self, products: list) -> str: # ✅ 
        """
        فرمت‌بندی لیست محصولات برای نمایش
        
        Args:
            products: لیست محصولات
            
        Returns:
            متن فرمت‌شده
        """
        if not products:
            return "📦 *موجودی محصولات*\n\n❌ هیچ محصولی ثبت نشده است."
        
        text = "📦 *موجودی محصولات*\n\n"
        for product in products:
            status_icon = "✅" if product['quantity'] > 0 else "❌"
            text += f"{status_icon} {product['name']} - موجودی: {product['quantity']} عدد\n"
        
        return text
    
    def format_product_details(self, product: dict) -> str:
        """
        فرمت‌بندی جزئیات محصول
        
        Args:
            product: داده‌های محصول
            
        Returns:
            متن فرمت‌شده
        """
        text = f"📦 محصول: {product['name']}\n"
        text += f"📊 موجودی: {product['quantity']} عدد\n"
        return text
    
    def get_available_products_text(self) -> str:
        """
        دریافت متن محصولات موجود برای فروش
        
        Returns:
            متن فرمت‌شده
        """
        available_products = self.data_manager.get_available_products()
        
        if not available_products:
            return "❌ هیچ محصولی برای فروش دسترس ندارد."
        
        text = "📦 *محصولات موجود برای فروش:*\n\n"
        for product in available_products:
            status_icon = "✅" if product['quantity'] > 0 else "❌"
            text += f"{status_icon} {product['name']} - موجودی: {product['quantity']} عدد\n"
        
        return text
    
    def calculate_inventory_summary(self) -> dict: # ✅ 
        """
        محاسبه خلاصه موجودی
        
        Returns:
            دیکشنری شامل: total_products, total_items, low_stock_products
        """
        products = self.data_manager.get_all_products()
        
        total_products = len(products)
        total_items = sum(p.get('quantity', 0) for p in products)
        low_stock = [p for p in products if 0 < p.get('quantity', 0) <= 5]
        
        return {
            'total_products': total_products,
            'total_items': total_items,
            'low_stock_products': low_stock,
            'low_stock_count': len(low_stock)
        }
    
    def delete_product(self, product_id: int) -> dict: # ✅ 
        """
        حذف محصول
        
        Args:
            product_id: شناسه محصول
            
        Returns:
            دیکشنری شامل: product (محصول حذف‌شده یا None)
        """
        validation = self.deletion_validator.validate_product_deletion(product_id)
        
        if not validation['is_valid']:
            return None
        
        product = validation['product']
        self.data_manager.delete_product(product_id)
        
        return product

    def update_product_name(self, product_id: int, new_name: str) -> dict: # ✅ 
        """
        بروزرسانی نام محصول
        
        Args:
            product_id: شناسه محصول
            new_name: نام جدید
            
        Returns:
            دیکشنری شامل: success (bool), product (dict|None), error_message (str|None)
        """
        # ولیدیشن نام
        name_validation = self.product_validator.validate_product_name(new_name)
        if not name_validation['is_valid']:
            return {
                'success': False,
                'product': None,
                'error_message': name_validation['error_message']
            }
        
        # ولیدیشن وجود محصول
        product_validation = self.product_validator.validate_product_exists(product_id)
        if not product_validation['is_valid']:
            return {
                'success': False,
                'product': None,
                'error_message': '❌ محصول یافت نشد.'
            }
        
        product = product_validation['product']
        old_name = product['name']
        
        # بروزرسانی
        self.data_manager.update_product_name(product_id, new_name)
        
        return {
            'success': True,
            'product': product,
            'old_name': old_name,
            'new_name': new_name,
            'error_message': None
        }
    
    def update_product_quantity(self, product_id: int, new_quantity: int) -> dict: # ✅ 
        """
        بروزرسانی موجودی محصول
        
        Args:
            product_id: شناسه محصول
            new_quantity: موجودی جدید
            
        Returns:
            دیکشنری شامل: success (bool), product (dict|None), error_message (str|None)
        """
        # ولیدیشن موجودی
        quantity_validation = self.product_validator.validate_product_quantity(new_quantity)
        if not quantity_validation['is_valid']:
            return {
                'success': False,
                'product': None,
                'error_message': quantity_validation['error_message']
            }
        
        # ولیدیشن وجود محصول
        product_validation = self.product_validator.validate_product_exists(product_id)
        if not product_validation['is_valid']:
            return {
                'success': False,
                'product': None,
                'error_message': '❌ محصول یافت نشد.'
            }
        
        product = product_validation['product']
        
        # بروزرسانی
        self.data_manager.update_product_quantity(product_id, new_quantity)
        
        return {
            'success': True,
            'product': product,
            'new_quantity': new_quantity,
            'error_message': None
        }
