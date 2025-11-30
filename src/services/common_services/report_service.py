"""
سرویس تولید گزارش‌ها
"""

from ...utils.pagination import paginate


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
        
        text += "\n📏 لیست کامل:\n"
        for product in products:
            qty = int(product['quantity'])
            status_icon = "✅" if qty > 0 else "❌"
            text += f"{status_icon} {product['name']}: {qty} عدد\n"
        
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
    
    def get_full_report_page(self, page: int = 1, items_per_page: int = 5) -> dict:
        """
        دریافت صفحه‌ای از گزارش کامل
        
        Args:
            page: شماره صفحه
            items_per_page: تعداد آیتم در هر صفحه
            
        Returns:
            دیکشنری شامل: text, page, total_pages
        """
        # دریافت تمام محصولات
        products = self.data_manager.get_all_products()
        
        # محاسبه خلاصه‌ها (ثابت در تمام صفحات)
        inventory_summary = self.inventory_service.calculate_inventory_summary()
        sales_summary = self.sales_service.calculate_sales_summary()
        
        # ساخت لیست محصولات برای صفحه‌بندی (کم‌موجود اول، سپس عادی)
        product_items = []
        
        # اضافه کردن محصولات کم‌موجود اول
        if inventory_summary['low_stock_products']:
            for product in inventory_summary['low_stock_products']:
                qty = int(product['quantity'])
                product_items.append({
                    'type': 'product',
                    'text': f"⚠️ {product['name']}: {qty} عدد"
                })
        
        # اضافه کردن باقی محصولات
        if products:
            for product in products:
                qty = int(product['quantity'])
                # اگر محصول در لیست کم‌موجود نیست
                if qty > 5:
                    status_icon = "✅"
                    product_items.append({
                        'type': 'product',
                        'text': f"{status_icon} {product['name']}: {qty} عدد"
                    })
        
        # صفحه‌بندی برای تمام محصولات
        pagination_result = paginate(product_items, page, items_per_page)
        
        # ساخت متن صفحه (خلاصه‌ها ثابت + محصولات صفحه‌بندی‌شده)
        text = f"📊 *گزارش کامل فروشگاه*\n\n"
        
        # خلاصه موجودی (ثابت)
        text += f"📦 *خلاصه موجودی*\n"
        text += f"• کل محصولات: {inventory_summary['total_products']}\n"
        text += f"• کل موجودی: {inventory_summary['total_items']} عدد\n"
        text += f"• محصولات کم‌موجود: {inventory_summary['low_stock_count']}\n\n"
        
        # لیست محصولات (صفحه‌بندی‌شده - کم‌موجود و عادی با هم)
        if product_items:
            text += f"📏 *لیست محصولات* (صفحه {pagination_result['page']}/{pagination_result['total_pages']})\n"
            for item in pagination_result['items']:
                text += item['text'] + "\n"
            text += "\n"
        
        # خلاصه فروش‌ها (ثابت)
        text += f"💳 *خلاصه فروش‌ها*\n"
        text += f"• تعداد فروش: {sales_summary['total_sales']}\n"
        text += f"• کل درآمد: {sales_summary['total_revenue']}\n"
        text += f"• کل هزینه: {sales_summary['total_cost']}\n"
        text += f"• هزینه‌های جانبی: {sales_summary['total_extra_cost']}\n"
        text += f"• سود خالص: {sales_summary['total_profit']}"
        
        return {
            'text': text,
            'page': pagination_result['page'],
            'total_pages': pagination_result['total_pages']
        }
