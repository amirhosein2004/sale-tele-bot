"""
سرویس مدیریت موجودی و محصولات
"""

from ...validations.deletion_validation import DeletionValidator
from ...validations.product_validation import ProductValidator
from ...utils.pagination import paginate


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
    
    def format_products_list(self, products: list) -> str: 
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
            quantity = int(product['quantity'])
            status_icon = "✅" if quantity > 0 else "❌"
            text += f"{status_icon} {product['name']} - موجودی: {quantity} عدد\n"
        
        return text
    
    def calculate_inventory_summary(self) -> dict: 
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

    def update_product_name(self, product_id: int, new_name: str) -> dict: 
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
        
        # استفاده از نام ولیدیشن‌شده
        validated_name = name_validation['name']
        
        # بروزرسانی
        self.data_manager.update_product_name(product_id, validated_name)
        
        return {
            'success': True,
            'product': product,
            'old_name': old_name,
            'new_name': validated_name,
            'error_message': None
        }
    
    def update_product_quantity(self, product_id: int, new_quantity: int) -> dict: 
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
        
        # استفاده از موجودی ولیدیشن‌شده
        validated_quantity = quantity_validation['quantity']
        
        # بروزرسانی
        self.data_manager.update_product_quantity(product_id, validated_quantity)
        
        return {
            'success': True,
            'product': product,
            'new_quantity': validated_quantity,
            'error_message': None
        }
    
    def create_product(self, product_name: str, quantity: int) -> dict:
        """
        ایجاد محصول جدید
        
        Args:
            product_name: نام محصول
            quantity: موجودی اولیه
            
        Returns:
            دیکشنری شامل: success (bool), product_id (int|None), error_message (str|None)
        """
        # ولیدیشن نام
        name_validation = self.product_validator.validate_product_name(product_name)
        if not name_validation['is_valid']:
            return {
                'success': False,
                'product_id': None,
                'error_message': name_validation['error_message']
            }
        
        # ولیدیشن موجودی
        quantity_validation = self.product_validator.validate_product_quantity(quantity)
        if not quantity_validation['is_valid']:
            return {
                'success': False,
                'product_id': None,
                'error_message': quantity_validation['error_message']
            }
        
        # استفاده از داده‌های ولیدیشن‌شده
        validated_name = name_validation['name']
        validated_quantity = quantity_validation['quantity']
        
        # اضافه کردن محصول
        product_id = self.data_manager.add_product(validated_name, validated_quantity)
        
        return {
            'success': True,
            'product_id': product_id,
            'product_name': validated_name,
            'quantity': validated_quantity,
            'error_message': None
        }
    
    def get_available_products_with_status(self) -> dict:
        """
        دریافت وضعیت محصولات برای فروش
        
        Returns:
            دیکشنری شامل: available_products (list), has_products (bool), message (str)
        """
        available_products = self.data_manager.get_available_products()
        
        if not available_products:
            all_products = self.data_manager.get_all_products()
            if not all_products:
                return {
                    'available_products': [],
                    'has_products': False,
                    'message': '❌ ابتدا باید محصول اضافه کنید.'
                }
            else:
                return {
                    'available_products': [],
                    'has_products': False,
                    'message': '❌ هیچ محصولی با موجودی کافی برای فروش وجود ندارد.\n\nلطفاً ابتدا موجودی محصولات را تکمیل کنید.'
                }
        
        return {
            'available_products': available_products,
            'has_products': True,
            'message': None
        }
    
    def get_inventory_page(self, page: int = 1, items_per_page: int = 5) -> dict:
        """
        دریافت صفحه‌ای از موجودی محصولات
        
        Args:
            page: شماره صفحه
            items_per_page: تعداد آیتم در هر صفحه
            
        Returns:
            دیکشنری شامل: products, page, total_pages, text
        """
        all_products = self.data_manager.get_all_products()
        
        if not all_products:
            return {
                'products': [],
                'page': 1,
                'total_pages': 1,
                'text': "📦 *موجودی محصولات*\n\n❌ هیچ محصولی ثبت نشده است."
            }
        
        # استفاده از تابع paginate
        pagination_result = paginate(all_products, page, items_per_page)
        
        # ساخت متن
        text = f"📦 *موجودی محصولات* (صفحه {pagination_result['page']}/{pagination_result['total_pages']})\n\n"
        for product in pagination_result['items']:
            quantity = int(product['quantity'])
            status_icon = "✅" if quantity > 0 else "❌"
            text += f"{status_icon} {product['name']} - موجودی: {quantity} عدد\n"
        
        return {
            'products': pagination_result['items'],
            'page': pagination_result['page'],
            'total_pages': pagination_result['total_pages'],
            'text': text
        }
    
    def get_products_for_edit(self) -> dict:
        """
        دریافت لیست محصولات برای ویرایش
        
        Returns:
            دیکشنری شامل: products, has_products, message
        """
        products = self.data_manager.get_all_products()
        
        if not products:
            return {
                'products': [],
                'has_products': False,
                'message': "❌ هیچ محصولی برای ویرایش وجود ندارد."
            }
        
        return {
            'products': products,
            'has_products': True,
            'message': None
        }
    
    def get_products_for_edit_page(self, page: int = 1, items_per_page: int = 5) -> dict:
        """
        دریافت صفحه‌ای از محصولات برای ویرایش
        
        Args:
            page: شماره صفحه
            items_per_page: تعداد آیتم در هر صفحه
            
        Returns:
            دیکشنری شامل: products, page, total_pages, text, has_products
        """
        all_products = self.data_manager.get_all_products()
        
        if not all_products:
            return {
                'products': [],
                'page': 1,
                'total_pages': 1,
                'text': "❌ هیچ محصولی برای ویرایش وجود ندارد.",
                'has_products': False
            }
        
        # استفاده از تابع paginate
        pagination_result = paginate(all_products, page, items_per_page)
        
        # ساخت متن
        text = f"✏️ *محصول مورد نظر را انتخاب کنید* (صفحه {pagination_result['page']}/{pagination_result['total_pages']})\n\n"
        for product in pagination_result['items']:
            quantity = int(product['quantity'])
            status_icon = "✅" if quantity > 0 else "❌"
            text += f"{status_icon} {product['name']} - موجودی: {quantity} عدد\n"
        
        return {
            'products': pagination_result['items'],
            'page': pagination_result['page'],
            'total_pages': pagination_result['total_pages'],
            'text': text,
            'has_products': True
        }
