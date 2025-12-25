"""
Adapter برای تبدیل Repository به interface مشابه DataManager
این کلاس به عنوان یک Adapter عمل می‌کند تا کدهای موجود بدون تغییر زیاد کار کنند
"""

from ..repository import RepositoryManager
from ..repository.converters import (
    product_to_dict,
    sale_to_dict,
    products_to_dict_list,
    sales_to_dict_list,
)


class DataManagerAdapter:
    """
    Adapter برای شبیه‌سازی رفتار DataManager با استفاده از Repository
    """

    def __init__(self):
        self.repo_manager = RepositoryManager()
        self.product_repo = self.repo_manager.product_repo
        self.sale_repo = self.repo_manager.sale_repo

    # ============ عملیات محصولات ============

    def add_product(self, name, quantity):
        """افزودن محصول جدید"""
        product, is_created = self.product_repo.create(name, int(quantity))
        return {
            'product_id': product.id,
            'is_created': is_created,
            'current_stock': product.stock
        }

    def get_all_products(self):
        """دریافت تمام محصولات"""
        products = self.product_repo.get_all()
        return products_to_dict_list(products)

    def get_product(self, product_id):
        """دریافت یک محصول"""
        product = self.product_repo.get_by_id(product_id)
        return product_to_dict(product)

    def get_by_id(self, product_id):
        """دریافت محصول با ID (برای سازگاری با ProductValidator)"""
        product = self.product_repo.get_by_id(product_id)
        return product

    def update_product_name(self, product_id, new_name):
        """به‌روزرسانی نام محصول"""
        return self.product_repo.update_name(product_id, new_name)

    def update_product_quantity(self, product_id, new_quantity):
        """به‌روزرسانی موجودی محصول"""
        return self.product_repo.update_stock(product_id, int(new_quantity))

    def delete_product(self, product_id):
        """حذف محصول"""
        return self.product_repo.delete(product_id)

    def get_products_text(self):
        """دریافت لیست محصولات به صورت متن"""
        products = self.get_all_products()
        if not products:
            return "📦 هیچ محصولی ثبت نشده است."

        text = "📦 *لیست محصولات و موجودی*\n\n"
        for product in products:
            text += f"🔹 {product['name']}\n"
            text += f"   موجودی: {product['quantity']} عدد\n\n"
        return text

    # ============ عملیات فروش‌ها ============

    def add_sale(self, sale_data):
        """افزودن فروش جدید"""
        sale = self.sale_repo.create(
            product_id=sale_data["product_id"],
            quantity=sale_data["quantity"],
            total_sale=sale_data["total_sale_price"],
            total_cost=sale_data["total_cost"],
            extra_cost=sale_data.get("extra_cost", 0.0),
        )
        return sale.id

    def get_all_sales(self):
        """دریافت تمام فروش‌ها"""
        sales = self.sale_repo.get_all(order_by_date=True)
        return sales_to_dict_list(sales)

    def get_sale(self, sale_id):
        """دریافت یک فروش"""
        sale = self.sale_repo.get_by_id(sale_id)
        return sale_to_dict(sale)

    def get_sale_by_id(self, sale_id):
        """دریافت فروش با ID (برای سازگاری با SaleValidator)"""
        sale = self.sale_repo.get_by_id(sale_id)
        return sale

    def update_sale(self, sale_id, sale_data):
        """به‌روزرسانی فروش"""
        # فقط پارامترهایی که در sale_data وجود دارند و None نیستند را ارسال کن
        update_params = {}
        
        if "product_id" in sale_data and sale_data["product_id"] is not None:
            update_params["product_id"] = sale_data["product_id"]
        if "quantity" in sale_data and sale_data["quantity"] is not None:
            update_params["quantity"] = sale_data["quantity"]
        if "total_sale_price" in sale_data and sale_data["total_sale_price"] is not None:
            update_params["total_sale"] = sale_data["total_sale_price"]
        if "total_cost" in sale_data and sale_data["total_cost"] is not None:
            update_params["total_cost"] = sale_data["total_cost"]
        if "extra_cost" in sale_data and sale_data["extra_cost"] is not None:
            update_params["extra_cost"] = sale_data["extra_cost"]
        
        return self.sale_repo.update(sale_id, **update_params)

    def delete_sale(self, sale_id):
        """حذف فروش"""
        return self.sale_repo.delete(sale_id)

    def get_sales_text(self):
        """دریافت لیست فروش‌ها به صورت متن"""
        sales = self.get_all_sales()
        if not sales:
            return "📊 هیچ فروشی ثبت نشده است."

        text = "📊 *لیست فروش‌ها*\n\n"
        text += "=" * 50 + "\n"

        total_revenue = 0
        total_cost = 0
        total_profit = 0

        for sale in sales:
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

            total_revenue += sale["total_sale_price"]
            total_cost += sale["total_cost"] + sale["extra_cost"]
            total_profit += sale["net_profit"]

        text += f"\n📊 *خلاصه کلی*\n"
        text += f"💰 کل فروش: {total_revenue}\n"
        text += f"💸 کل هزینه: {total_cost}\n"
        text += f"📈 کل سود: {total_profit}\n"

        return text

    # ============ مدیریت موجودی ============

    def reduce_inventory(self, product_id, quantity):
        """کم کردن موجودی محصول"""
        return self.product_repo.reduce_stock(product_id, quantity)

    def increase_inventory(self, product_id, quantity):
        """اضافه کردن موجودی محصول"""
        return self.product_repo.increase_stock(product_id, quantity)

    def check_inventory(self, product_id, quantity):
        """بررسی موجودی کافی"""
        return self.product_repo.check_stock_availability(product_id, quantity)

    def check_stock_availability(self, product_id, quantity):
        """بررسی موجودی کافی (برای سازگاری با SaleInputValidator)"""
        return self.product_repo.check_stock_availability(product_id, quantity)

    def get_available_products(self):
        """دریافت محصولات با موجودی بیش از صفر"""
        products = self.product_repo.get_available_products()
        return products_to_dict_list(products)

    def find_product_by_name(self, product_name):
        """پیدا کردن محصول با نام"""
        product = self.product_repo.get_by_name(product_name)
        return product_to_dict(product)

    def close(self):
        """بستن اتصالات"""
        self.repo_manager.close()
