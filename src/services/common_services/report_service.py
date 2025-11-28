"""
سرویس تولید گزارش‌ها
"""


class ReportService:
    """سرویس تولید و فرمت‌بندی گزارش‌ها"""
    
    def __init__(self, data_manager, inventory_service, sales_service):
        """
        Args:
            data_manager: مدیریت‌کننده داده‌ها
            inventory_service: سرویس موجودی
            sales_service: سرویس فروش
        """
        self.data_manager = data_manager
        self.inventory_service = inventory_service
        self.sales_service = sales_service
    
    def generate_inventory_report(self) -> str:
        """
        تولید گزارش موجودی
        
        Returns:
            متن گزارش
        """
        products = self.data_manager.get_all_products()
        
        if not products:
            return "📦 *گزارش موجودی*\n\n❌ هیچ محصولی ثبت نشده است."
        
        summary = self.inventory_service.calculate_inventory_summary()
        
        text = "📦 *گزارش موجودی محصولات*\n\n"
        text += f"📊 کل محصولات: {summary['total_products']}\n"
        text += f"📈 کل موجودی: {summary['total_items']} عدد\n"
        
        if summary['low_stock_count'] > 0:
            text += f"\n⚠️ محصولات کم‌موجود ({summary['low_stock_count']}):\n"
            for product in summary['low_stock_products']:
                text += f"  • {product['name']}: {product['quantity']} عدد\n"
        
        text += "\n📝 لیست کامل:\n"
        for product in products:
            status_icon = "✅" if product['quantity'] > 0 else "❌"
            text += f"{status_icon} {product['name']}: {product['quantity']} عدد\n"
        
        return text
    
    def generate_sales_report(self) -> str:
        """
        تولید گزارش فروش‌ها
        
        Returns:
            متن گزارش
        """
        sales = self.data_manager.get_all_sales()
        
        if not sales:
            return "💳 *گزارش فروش‌ها*\n\n❌ هیچ فروشی ثبت نشده است."
        
        summary = self.sales_service.calculate_sales_summary()
        
        text = "💳 *گزارش فروش‌ها*\n\n"
        text += f"📊 تعداد فروش: {summary['total_sales']}\n"
        text += f"💰 کل درآمد: {summary['total_revenue']}\n"
        text += f"💸 کل هزینه: {summary['total_cost']}\n"
        text += f"🏷️ هزینه‌های جانبی: {summary['total_extra_cost']}\n"
        text += f"📈 سود خالص: {summary['total_profit']}\n"
        
        return text
    
    def generate_full_report(self) -> str:
        """
        تولید گزارش کامل
        
        Returns:
            متن گزارش کامل
        """
        inventory_report = self.generate_inventory_report()
        sales_report = self.generate_sales_report()
        
        return f"📊 *گزارش کامل فروشگاه*\n\n{inventory_report}\n\n{sales_report}"
    
    def generate_summary_report(self) -> str:
        """
        تولید گزارش خلاصه
        
        Returns:
            متن گزارش خلاصه
        """
        inventory_summary = self.inventory_service.calculate_inventory_summary()
        sales_summary = self.sales_service.calculate_sales_summary()
        
        text = "📊 *گزارش خلاصه*\n\n"
        text += "📦 *موجودی:*\n"
        text += f"  • کل محصولات: {inventory_summary['total_products']}\n"
        text += f"  • کل موجودی: {inventory_summary['total_items']} عدد\n"
        text += f"  • محصولات کم‌موجود: {inventory_summary['low_stock_count']}\n"
        
        text += "\n💳 *فروش:*\n"
        text += f"  • تعداد فروش: {sales_summary['total_sales']}\n"
        text += f"  • کل درآمد: {sales_summary['total_revenue']}\n"
        text += f"  • سود خالص: {sales_summary['total_profit']}\n"
        
        return text
   
    def generate_product_report(self, product_name: str) -> str:
        """
        تولید گزارش محصول
        
        Args:
            product_name: نام محصول
            
        Returns:
            متن گزارش
        """
        product = self.data_manager.find_product_by_name(product_name)
        
        if not product:
            return f"❌ محصول '{product_name}' یافت نشد."
        
        sales = self.sales_service.get_sales_by_product(product_name)
        profit = self.sales_service.calculate_product_profit(product_name)
        
        text = f"📦 *گزارش محصول: {product_name}*\n\n"
        text += f"📊 موجودی فعلی: {product['quantity']} عدد\n"
        text += f"💳 تعداد فروش: {len(sales)}\n"
        text += f"📈 سود کل: {profit}\n"
        
        return text
