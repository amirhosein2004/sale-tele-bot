"""
سرویس مدیریت فروش‌ها و محاسبات
"""

from ...validations.deletion_validation import DeletionValidator
from ...validations.sale_validation import SaleValidator, SaleInputValidator
from ...utils.pagination import paginate


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

    def format_sale_details(self, sale: dict) -> str: # 
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
    
    def calculate_sales_summary(self) -> dict: 
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
    
    def delete_sale(self, sale_id: int) -> dict: 
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
    
    def get_sale_details(self, sale_id: int) -> dict: 
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

    def create_sale(self, sale_data: dict) -> dict: 
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
        
        # ولیدیشن تاریخ
        date_validation = self.input_validator.validate_sale_date(sale_data.get('date', ''))
        if not date_validation['is_valid']:
            return {
                'success': False,
                'sale_id': None,
                'summary': None,
                'error_message': date_validation['error_message'],
                'remaining_qty': None
            }
        
        # ولیدیشن قیمت
        price_validation = self.input_validator.validate_sale_price(sale_data.get('total_sale_price', 0))
        if not price_validation['is_valid']:
            return {
                'success': False,
                'sale_id': None,
                'summary': None,
                'error_message': price_validation['error_message'],
                'remaining_qty': None
            }
        
        # ولیدیشن هزینه خرید
        cost_validation = self.input_validator.validate_sale_cost(sale_data.get('total_cost', 0))
        if not cost_validation['is_valid']:
            return {
                'success': False,
                'sale_id': None,
                'summary': None,
                'error_message': cost_validation['error_message'],
                'remaining_qty': None
            }
        
        # ولیدیشن هزینه جانبی
        extra_cost_validation = self.input_validator.validate_sale_extra_cost(sale_data.get('extra_cost', 0))
        if not extra_cost_validation['is_valid']:
            return {
                'success': False,
                'sale_id': None,
                'summary': None,
                'error_message': extra_cost_validation['error_message'],
                'remaining_qty': None
            }
        
        # استفاده از داده‌های ولیدیشن‌شده
        sale_data['date'] = date_validation['date']
        sale_data['total_sale_price'] = price_validation['price']
        sale_data['total_cost'] = cost_validation['cost']
        sale_data['extra_cost'] = extra_cost_validation['extra_cost']
        
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
    
    def update_sale(self, sale_id: int, sale_data: dict) -> dict: 
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
        
        # ولیدیشن تاریخ
        date_validation = self.input_validator.validate_sale_date(sale_data.get('date', ''))
        if not date_validation['is_valid']:
            return {
                'success': False,
                'error_message': date_validation['error_message']
            }
        
        # ولیدیشن قیمت
        price_validation = self.input_validator.validate_sale_price(sale_data.get('total_sale_price', 0))
        if not price_validation['is_valid']:
            return {
                'success': False,
                'error_message': price_validation['error_message']
            }
        
        # ولیدیشن هزینه خرید
        cost_validation = self.input_validator.validate_sale_cost(sale_data.get('total_cost', 0))
        if not cost_validation['is_valid']:
            return {
                'success': False,
                'error_message': cost_validation['error_message']
            }
        
        # ولیدیشن هزینه جانبی
        extra_cost_validation = self.input_validator.validate_sale_extra_cost(sale_data.get('extra_cost', 0))
        if not extra_cost_validation['is_valid']:
            return {
                'success': False,
                'error_message': extra_cost_validation['error_message']
            }
        
        # استفاده از داده‌های ولیدیشن‌شده
        sale_data['date'] = date_validation['date']
        sale_data['total_sale_price'] = price_validation['price']
        sale_data['total_cost'] = cost_validation['cost']
        sale_data['extra_cost'] = extra_cost_validation['extra_cost']
        
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
    
    def get_sales_page(self, page: int = 1, items_per_page: int = 5) -> dict:
        """
        دریافت صفحه‌ای از فروش‌ها برای نمایش
        
        Args:
            page: شماره صفحه
            items_per_page: تعداد آیتم در هر صفحه
            
        Returns:
            دیکشنری شامل: sales, page, total_pages, text, has_sales, message
        """
        all_sales = self.data_manager.get_all_sales()
        
        if not all_sales:
            return {
                'sales': [],
                'page': 1,
                'total_pages': 1,
                'text': '📊 هیچ فروشی ثبت نشده است.',
                'has_sales': False,
                'message': '📊 هیچ فروشی ثبت نشده است.'
            }
        
        # استفاده از تابع paginate
        pagination_result = paginate(all_sales, page, items_per_page)
        
        # ساخت متن
        text = f"📊 *لیست فروش‌ها* (صفحه {pagination_result['page']}/{pagination_result['total_pages']})\n\n"
        text += "فروش مورد نظر را انتخاب کنید:"
        
        return {
            'sales': pagination_result['items'],
            'page': pagination_result['page'],
            'total_pages': pagination_result['total_pages'],
            'text': text,
            'has_sales': True,
            'message': None
        }

    def get_products_for_sale_page(self, page: int = 1, items_per_page: int = 5) -> dict:
        """
        دریافت صفحه‌ای از محصولات برای فروش
        
        Args:
            page: شماره صفحه
            items_per_page: تعداد آیتم در هر صفحه
            
        Returns:
            دیکشنری شامل: products, page, total_pages, text, has_products, message
        """
        available_products = self.data_manager.get_available_products()
        
        if not available_products:
            all_products = self.data_manager.get_all_products()
            if not all_products:
                return {
                    'products': [],
                    'page': 1,
                    'total_pages': 1,
                    'text': '❌ ابتدا باید محصول اضافه کنید.',
                    'has_products': False,
                    'message': '❌ ابتدا باید محصول اضافه کنید.'
                }
            else:
                return {
                    'products': [],
                    'page': 1,
                    'total_pages': 1,
                    'text': '❌ هیچ محصولی با موجودی کافی برای فروش وجود ندارد.\n\nلطفاً ابتدا موجودی محصولات را تکمیل کنید.',
                    'has_products': False,
                    'message': '❌ هیچ محصولی با موجودی کافی برای فروش وجود ندارد.\n\nلطفاً ابتدا موجودی محصولات را تکمیل کنید.'
                }
        
        # استفاده از تابع paginate
        pagination_result = paginate(available_products, page, items_per_page)
        
        # ساخت متن
        text = f"📝 *محصول مورد نظر را از لیست زیر انتخاب کنید* (صفحه {pagination_result['page']}/{pagination_result['total_pages']})\n\n"
        for product in pagination_result['items']:
            quantity = int(product['quantity'])
            text += f"✅ {product['name']} ({quantity} عدد)\n"
        
        return {
            'products': pagination_result['items'],
            'page': pagination_result['page'],
            'total_pages': pagination_result['total_pages'],
            'text': text,
            'has_products': True,
            'message': None
        }
