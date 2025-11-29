"""
سرویس مدیریت فروش‌ها و محاسبات
"""

from ...validations.deletion_validation import DeletionValidator
from ...validations.sale_validation import SaleValidator, SaleInputValidator


class SalesService:
    """سرویس عملیات فروش"""
    
    def __init__(self, data_manager):
        """
        Args:
            data_manager: مدیریت‌کننده داده‌ها
        """
        self.data_manager = data_manager
        self.deletion_validator = DeletionValidator(data_manager)
        self.sale_validator = SaleValidator(data_manager)
        self.input_validator = SaleInputValidator(data_manager)
    
    def calculate_profit(self, total_sale_price: float, total_cost: float, extra_cost: float) -> float:
        """
        محاسبه سود خالص
        
        Args:
            total_sale_price: کل قیمت فروش
            total_cost: کل هزینه خرید
            extra_cost: هزینه‌های جانبی
            
        Returns:
            سود خالص
        """
        return total_sale_price - total_cost - extra_cost
    
    def calculate_unit_price(self, total_price: float, quantity: int) -> float:
        """
        محاسبه قیمت واحد
        
        Args:
            total_price: کل قیمت
            quantity: تعداد
            
        Returns:
            قیمت واحد
        """
        if quantity <= 0:
            return 0.0
        return total_price / quantity
    
    def format_sale_details(self, sale: dict) -> str: # ✅
        """
        فرمت‌بندی جزئیات فروش
        
        Args:
            sale: داده‌های فروش
            
        Returns:
            متن فرمت‌شده
        """
        text = f"🧾 فروش شماره {sale['id']}\n"
        text += f"📦 محصول: {sale['product_name']}\n"
        text += f"🔢 تعداد: {sale['quantity']}\n"
        text += f"💵 قیمت واحد: {sale['sale_price']}\n"
        text += f"💰 کل فروش: {sale['total_sale_price']}\n"
        text += f"💸 کل خرید: {sale['total_cost']}\n"
        text += f"🏷️ هزینه‌های جانبی: {sale['extra_cost']}\n"
        text += f"📈 سود خالص: {sale['net_profit']}\n"
        text += f"📅 تاریخ: {sale['date']}\n"
        return text
    
    def format_sale_summary(self, sale_data: dict) -> str: 
        """
        فرمت‌بندی خلاصه فروش
        
        Args:
            sale_data: داده‌های فروش
            
        Returns:
            متن فرمت‌شده
        """
        return (
            "✅ *فروش ثبت شد*\n\n"
            f"📦 محصول: {sale_data['product_name']}\n"
            f"🔢 تعداد: {sale_data['quantity']}\n"
            f"💵 قیمت واحد: {sale_data['sale_price']}\n"
            f"💰 کل فروش: {sale_data['total_sale_price']}\n"
            f"💸 کل خرید: {sale_data['total_cost']}\n"
            f"🏷️ هزینه‌های جانبی: {sale_data['extra_cost']}\n"
            f"📈 سود خالص: {sale_data['net_profit']}\n"
            f"📅 تاریخ: {sale_data['date']}\n"
        )
    
    def calculate_sales_summary(self) -> dict: # ✅ 
        """
        محاسبه خلاصه فروش‌ها
        
        Returns:
            دیکشنری شامل: total_sales, total_revenue, total_cost, total_profit
        """
        sales = self.data_manager.get_all_sales()
        
        total_sales = len(sales)
        total_revenue = sum(s.get('total_sale_price', 0) for s in sales)
        total_cost = sum(s.get('total_cost', 0) for s in sales)
        total_extra_cost = sum(s.get('extra_cost', 0) for s in sales)
        total_profit = total_revenue - total_cost - total_extra_cost
        
        return {
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_extra_cost': total_extra_cost,
            'total_profit': total_profit
        }
    
    def get_sales_by_product(self, product_name: str) -> list:
        """
        دریافت فروش‌های یک محصول
        
        Args:
            product_name: نام محصول
            
        Returns:
            لیست فروش‌های محصول
        """
        sales = self.data_manager.get_all_sales()
        return [s for s in sales if s.get('product_name') == product_name]
    
    def calculate_product_profit(self, product_name: str) -> float:
        """
        محاسبه سود کل یک محصول
        
        Args:
            product_name: نام محصول
            
        Returns:
            سود کل محصول
        """
        sales = self.get_sales_by_product(product_name)
        return sum(s.get('net_profit', 0) for s in sales)
    
    def delete_sale(self, sale_id: int) -> dict: # ✅ 
        """
        حذف فروش و بازگرداندن موجودی
        
        Args:
            sale_id: شناسه فروش
            
        Returns:
            دیکشنری شامل: sale (فروش حذف‌شده یا None)
        """
        validation = self.deletion_validator.validate_sale_deletion(sale_id)
        
        if not validation['is_valid']:
            return None
        
        sale = validation['sale']
        
        # بازگرداندن موجودی
        if 'product_id' in sale:
            product = self.data_manager.find_product_by_name(sale['product_name'])
            if product:
                self.data_manager.increase_inventory(product['id'], sale['quantity'])
        
        # حذف فروش
        self.data_manager.delete_sale(sale_id)
        
        return sale
    
    def get_sale_details(self, sale_id: int) -> dict: # ✅
        """
        دریافت جزئیات فروش
        
        Args:
            sale_id: شناسه فروش
            
        Returns:
            دیکشنری شامل: success (bool), sale (dict|None), text (str|None)
        """
        validation = self.sale_validator.validate_sale_exists(sale_id)
        
        if not validation['is_valid']:
            return {
                'success': False,
                'sale': None,
                'text': '❌ فروش یافت نشد.'
            }
        
        sale = validation['sale']
        text = self.format_sale_details(sale)
        text += "\n\nچه کاری می‌خواهید انجام دهید?"
        
        return {
            'success': True,
            'sale': sale,
            'text': text
        }

    def create_sale(self, sale_data: dict) -> dict: # ✅
        """
        ایجاد فروش جدید
        
        Args:
            sale_data: داده‌های فروش
            
        Returns:
            دیکشنری شامل: success (bool), sale_id (int|None), summary (str|None), error_message (str|None), remaining_qty (int|None)
        """
        product_id = sale_data.get('product_id')
        quantity = sale_data.get('quantity')
        
        # ولیدیشن دسترسی محصول
        availability = self.input_validator.validate_product_availability(product_id, quantity)
        if not availability['is_valid']:
            return {
                'success': False,
                'sale_id': None,
                'summary': None,
                'error_message': availability['error_message'],
                'remaining_qty': None
            }
        
        # کم کردن موجودی
        if not self.data_manager.reduce_inventory(product_id, quantity):
            return {
                'success': False,
                'sale_id': None,
                'summary': None,
                'error_message': '❌ خطا در کم کردن موجودی! لطفاً دوباره تلاش کنید.',
                'remaining_qty': None
            }
        
        # اضافه کردن فروش
        sale_id = self.data_manager.add_sale(sale_data)
        
        # دریافت موجودی باقی‌مانده
        current_product = self.data_manager.get_product(product_id)
        remaining_qty = current_product['quantity'] if current_product else 0
        
        # فرمت‌بندی خلاصه
        summary = self.format_sale_summary(sale_data)
        summary += f"\n📦 موجودی باقی‌مانده: {remaining_qty} عدد"
        
        return {
            'success': True,
            'sale_id': sale_id,
            'summary': summary,
            'error_message': None,
            'remaining_qty': remaining_qty
        }
    
    def update_sale(self, sale_id: int, sale_data: dict) -> dict: # ✅
        """
        بروزرسانی فروش
        
        Args:
            sale_id: شناسه فروش
            sale_data: داده‌های جدید فروش
            
        Returns:
            دیکشنری شامل: success (bool), error_message (str|None)
        """
        # ولیدیشن وجود فروش
        validation = self.sale_validator.validate_sale_exists(sale_id)
        if not validation['is_valid']:
            return {
                'success': False,
                'error_message': '❌ فروش یافت نشد.'
            }
        
        # محاسبه سود خالص
        sale_data['net_profit'] = sale_data['total_sale_price'] - sale_data['total_cost'] - sale_data['extra_cost']
        
        # بروزرسانی
        if self.data_manager.update_sale(sale_id, sale_data):
            return {
                'success': True,
                'error_message': None
            }
        
        return {
            'success': False,
            'error_message': '❌ خطا در بروزرسانی فروش!'
        }
    
    def get_sales_list_for_display(self) -> dict: # ✅
        """
        دریافت لیست فروش‌ها برای نمایش
        
        Returns:
            دیکشنری شامل: has_sales (bool), sales (list), message (str)
        """
        sales = self.data_manager.get_all_sales()
        
        if not sales:
            return {
                'has_sales': False,
                'sales': [],
                'message': '📊 هیچ فروشی ثبت نشده است.'
            }
        
        return {
            'has_sales': True,
            'sales': sales,
            'message': None
        }
