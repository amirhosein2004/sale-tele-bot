# مدیریت داده‌های محصولات و فروش‌ها

class DataManager:
    """کلاس برای مدیریت داده‌های محصولات و فروش‌ها در حافظه موقت"""
    
    def __init__(self):
        self.products = {}  # {product_id: {'name': str, 'quantity': int}}
        self.sales = []     # لیست فروش‌ها
        self.product_counter = 0
        self.sale_counter = 0
    
    # ============ عملیات محصولات ============
    
    def add_product(self, name, quantity):
        """افزودن محصول جدید"""
        self.product_counter += 1
        product_id = self.product_counter
        self.products[product_id] = {
            'id': product_id,
            'name': name,
            'quantity': quantity
        }
        return product_id
    
    def get_all_products(self):
        """دریافت تمام محصولات"""
        return list(self.products.values())
    
    def get_product(self, product_id):
        """دریافت یک محصول"""
        return self.products.get(product_id)
    
    def update_product_name(self, product_id, new_name):
        """به‌روزرسانی نام محصول"""
        if product_id in self.products:
            self.products[product_id]['name'] = new_name
            return True
        return False
    
    def update_product_quantity(self, product_id, new_quantity):
        """به‌روزرسانی موجودی محصول"""
        if product_id in self.products:
            self.products[product_id]['quantity'] = new_quantity
            return True
        return False
    
    def delete_product(self, product_id):
        """حذف محصول"""
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False
    
    def get_products_text(self):
        """دریافت لیست محصولات به صورت متن"""
        if not self.products:
            return "📦 هیچ محصولی ثبت نشده است."
        
        text = "📦 *لیست محصولات و موجودی*\n\n"
        for product in self.get_all_products():
            text += f"🔹 {product['name']}\n"
            text += f"   موجودی: {product['quantity']} عدد\n\n"
        return text
    
    # ============ عملیات فروش‌ها ============
    
    def add_sale(self, sale_data):
        """افزودن فروش جدید"""
        self.sale_counter += 1
        sale_data['id'] = self.sale_counter
        self.sales.append(sale_data)
        return self.sale_counter
    
    def get_all_sales(self):
        """دریافت تمام فروش‌ها"""
        return self.sales
    
    def get_sale(self, sale_id):
        """دریافت یک فروش"""
        for sale in self.sales:
            if sale['id'] == sale_id:
                return sale
        return None
    
    def update_sale(self, sale_id, sale_data):
        """به‌روزرسانی فروش"""
        for i, sale in enumerate(self.sales):
            if sale['id'] == sale_id:
                sale_data['id'] = sale_id
                self.sales[i] = sale_data
                return True
        return False
    
    def delete_sale(self, sale_id):
        """حذف فروش"""
        for i, sale in enumerate(self.sales):
            if sale['id'] == sale_id:
                del self.sales[i]
                return True
        return False
    
    def get_sales_text(self):
        """دریافت لیست فروش‌ها به صورت متن"""
        if not self.sales:
            return "📊 هیچ فروشی ثبت نشده است."
        
        text = "📊 *لیست فروش‌ها*\n\n"
        text += "=" * 50 + "\n"
        
        total_revenue = 0
        total_cost = 0
        total_profit = 0
        
        for sale in self.sales:
            text += f"\n🔹 فروش شماره {sale['id']}\n"
            text += f"📦 محصول: {sale['product_name']}\n"
            text += f"🔢 تعداد: {sale['quantity']}\n"
            text += f"💵 قیمت فروش: {sale['sale_price']}\n"
            text += f"💰 کل فروش: {sale['total_sale_price']}\n"
            text += f"💸 کل خرید: {sale['total_cost']}\n"
            text += f"🏷️ هزینه‌های جانبی: {sale['extra_cost']}\n"
            text += f"📈 سود خالص: {sale['net_profit']}\n"
            text += f"📅 تاریخ: {sale['date']}\n"
            text += "-" * 50 + "\n"
            
            total_revenue += sale['total_sale_price']
            total_cost += sale['total_cost'] + sale['extra_cost']
            total_profit += sale['net_profit']
        
        text += f"\n📊 *خلاصه کلی*\n"
        text += f"💰 کل فروش: {total_revenue}\n"
        text += f"💸 کل هزینه: {total_cost}\n"
        text += f"📈 کل سود: {total_profit}\n"
        
        return text
    
    def get_sales_summary(self):
        """دریافت خلاصه فروش‌ها"""
        if not self.sales:
            return "📊 هیچ فروشی ثبت نشده است."
        
        total_revenue = 0
        total_cost = 0
        total_profit = 0
        
        for sale in self.sales:
            total_revenue += sale['total_sale_price']
            total_cost += sale['total_cost'] + sale['extra_cost']
            total_profit += sale['net_profit']
        
        text = f"📊 *خلاصه فروش‌ها*\n\n"
        text += f"🔢 تعداد فروش: {len(self.sales)}\n"
        text += f"💰 کل فروش: {total_revenue}\n"
        text += f"💸 کل هزینه: {total_cost}\n"
        text += f"📈 کل سود: {total_profit}\n"
        
        return text
    
    # ============ مدیریت موجودی ============
    
    def reduce_inventory(self, product_id, quantity):
        """کم کردن موجودی محصول"""
        if product_id in self.products:
            current_qty = int(self.products[product_id]['quantity'])
            if current_qty >= quantity:
                self.products[product_id]['quantity'] = current_qty - quantity
                return True
        return False
    
    def increase_inventory(self, product_id, quantity):
        """اضافه کردن موجودی محصول"""
        if product_id in self.products:
            current_qty = int(self.products[product_id]['quantity'])
            self.products[product_id]['quantity'] = current_qty + quantity
            return True
        return False
    
    def check_inventory(self, product_id, quantity):
        """بررسی موجودی کافی"""
        if product_id in self.products:
            current_qty = int(self.products[product_id]['quantity'])
            return current_qty >= quantity
        return False
    
    def get_available_products(self):
        """دریافت محصولات با موجودی بیش از صفر"""
        available_products = []
        for product in self.get_all_products():
            if int(product['quantity']) > 0:
                available_products.append(product)
        return available_products
    
    def find_product_by_name(self, product_name):
        """پیدا کردن محصول با نام"""
        for product in self.get_all_products():
            if product['name'] == product_name:
                return product
        return None
