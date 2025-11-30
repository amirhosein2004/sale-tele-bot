"""
ولیدیشن‌های فروش
"""


class SaleValidator:
    """ولیدیشن عملیات فروش"""
    
    def __init__(self, data_manager):
        """
        Args:
            data_manager: مدیریت‌کننده داده‌ها
        """
        self.data_manager = data_manager
    
    def validate_sale_exists(self, sale_id: int) -> dict: # ✅
        """
        ولیدیشن وجود فروش
        
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


class SaleInputValidator:
    """ولیدیشن ورودی‌های فروش"""
    
    def __init__(self, data_manager):
        """
        Args:
            data_manager: مدیریت‌کننده داده‌ها
        """
        self.data_manager = data_manager
    
    def validate_sale_quantity(self, quantity: int, available_quantity: int) -> dict:
        """
        ولیدیشن تعداد فروش
        
        Args:
            quantity: تعداد درخواستی
            available_quantity: موجودی موجود
            
        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None), quantity (int|None)
        """
        try:
            qty = int(quantity)
            if qty <= 0:
                raise ValueError("تعداد باید مثبت باشد")
            
            # بررسی حد معقول (حداکثر 1 میلیون)
            if qty > 1_000_000:
                raise ValueError("تعداد بیش از حد است")
                
        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error_message': '❌ لطفاً عدد صحیح و مثبت وارد کنید.'
            }
        
        if qty > available_quantity:
            return {
                'is_valid': False,
                'error_message': f'❌ موجودی کافی نیست!\n\n📦 موجودی فعلی: {available_quantity} عدد\n🔢 درخواست شما: {qty} عدد\n\nلطفاً تعداد کمتری وارد کنید:'
            }
        
        return {
            'is_valid': True,
            'error_message': None,
            'quantity': qty
        }
    
    def validate_sale_price(self, price: float) -> dict:
        """
        ولیدیشن قیمت فروش
        
        Args:
            price: قیمت فروش
            
        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None), price (float|None)
        """
        try:
            price_value = float(price)
            if price_value <= 0:
                raise ValueError("قیمت باید مثبت باشد")
            
            # بررسی حد معقول (حداکثر 1 میلیارد)
            if price_value > 1_000_000_000:
                raise ValueError("قیمت بیش از حد است")
                
        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error_message': '❌ لطفاً عدد صحیح و مثبت وارد کنید.'
            }
        
        return {
            'is_valid': True,
            'error_message': None,
            'price': price_value
        }
    
    def validate_sale_cost(self, cost: float) -> dict:
        """
        ولیدیشن هزینه خرید
        
        Args:
            cost: هزینه خرید
            
        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None), cost (float|None)
        """
        try:
            cost_value = float(cost)
            if cost_value < 0:
                raise ValueError("هزینه نمی‌تواند منفی باشد")
            
            # بررسی حد معقول (حداکثر 1 میلیارد)
            if cost_value > 1_000_000_000:
                raise ValueError("هزینه بیش از حد است")
                
        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error_message': '❌ لطفاً عدد صحیح و مثبت وارد کنید.'
            }
        
        return {
            'is_valid': True,
            'error_message': None,
            'cost': cost_value
        }
    
    def validate_sale_extra_cost(self, extra_cost: float) -> dict:
        """
        ولیدیشن هزینه‌های جانبی
        
        Args:
            extra_cost: هزینه‌های جانبی
            
        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None), extra_cost (float|None)
        """
        try:
            extra_cost_value = float(extra_cost)
            if extra_cost_value < 0:
                raise ValueError("هزینه جانبی نمی‌تواند منفی باشد")
            
            # بررسی حد معقول (حداکثر 1 میلیارد)
            if extra_cost_value > 1_000_000_000:
                raise ValueError("هزینه جانبی بیش از حد است")
                
        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error_message': '❌ لطفاً عدد صحیح و مثبت وارد کنید.'
            }
        
        return {
            'is_valid': True,
            'error_message': None,
            'extra_cost': extra_cost_value
        }
    
    def validate_sale_date(self, date: str) -> dict:
        """
        ولیدیشن تاریخ فروش (فرمت: YYYY/MM/DD)
        
        Args:
            date: تاریخ فروش
            
        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None), date (str|None)
        """
        if not date or not date.strip():
            return {
                'is_valid': False,
                'error_message': '❌ تاریخ نمی‌تواند خالی باشد.'
            }
        
        date_str = date.strip()
        
        # بررسی فرمت YYYY/MM/DD
        parts = date_str.split('/')
        if len(parts) != 3:
            return {
                'is_valid': False,
                'error_message': '❌ فرمت تاریخ اشتباه است.\n\n📅 لطفاً به این صورت وارد کنید: 1403/09/29'
            }
        
        try:
            year, month, day = parts
            year_int = int(year)
            month_int = int(month)
            day_int = int(day)
            
            # بررسی محدوده‌های معقول
            if year_int < 1300 or year_int > 1500:
                raise ValueError("سال نامعتبر")
            
            if month_int < 1 or month_int > 12:
                raise ValueError("ماه نامعتبر")
            
            if day_int < 1 or day_int > 31:
                raise ValueError("روز نامعتبر")
            
        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error_message': '❌ فرمت تاریخ اشتباه است.\n\n📅 لطفاً به این صورت وارد کنید: 1403/09/29'
            }
        
        return {
            'is_valid': True,
            'error_message': None,
            'date': date_str
        }
    
    def validate_product_availability(self, product_id: int, quantity: int) -> dict:
        """
        ولیدیشن دسترسی محصول برای فروش
        
        Args:
            product_id: شناسه محصول
            quantity: تعداد درخواستی
            
        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None), product (dict|None)
        """
        product = self.data_manager.get_product(product_id)
        
        if not product:
            return {
                'is_valid': False,
                'error_message': '❌ محصول یافت نشد.',
                'product': None
            }
        
        if product['quantity'] <= 0:
            return {
                'is_valid': False,
                'error_message': f"❌ محصول '{product['name']}' موجودی ندارد.\n\nلطفاً محصول دیگری انتخاب کنید یا ابتدا موجودی را تکمیل کنید.",
                'product': product
            }
        
        if not self.data_manager.check_inventory(product_id, quantity):
            current_qty = product['quantity']
            return {
                'is_valid': False,
                'error_message': f"❌ خطا در ثبت فروش!\n\nموجودی کافی نیست:\n📦 موجودی فعلی: {current_qty} عدد\n🔢 درخواست شما: {quantity} عدد\n\nلطفاً دوباره تلاش کنید.",
                'product': product
            }
        
        return {
            'is_valid': True,
            'error_message': None,
            'product': product
        }
