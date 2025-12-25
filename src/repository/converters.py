"""
توابع تبدیل models به dictionary
"""

from ..models.product_model import Product
from ..models.sale_model import Sale


def product_to_dict(product: Product) -> dict:
    """
    تبدیل Product model به dictionary

    Args:
        product: Product instance

    Returns:
        dictionary شامل اطلاعات محصول
    """
    if not product:
        return None

    return {
        "id": product.id,
        "name": product.name,
        "quantity": product.stock,
        "stock": product.stock,
        "created_at": product.created_at,
    }


def sale_to_dict(sale: Sale) -> dict:
    """
    تبدیل Sale model به dictionary

    Args:
        sale: Sale instance

    Returns:
        dictionary شامل اطلاعات فروش
    """
    if not sale:
        return None
    
    # بررسی اینکه sale واقعاً یک Sale object است
    if not hasattr(sale, 'total_sale'):
        return None
    
    try:
        # اگر محصول وجود ندارد، نام را "نامشخص" قرار بده
        product_name = "نامشخص"
        try:
            if sale.product:
                product_name = sale.product.name
        except Exception:
            # اگر lazy loading خطا داد، نام را "نامشخص" بگذار
            pass

        net_profit = sale.total_sale - sale.total_cost - (sale.extra_cost or 0)
        sale_price = sale.total_sale / sale.quantity if sale.quantity > 0 else 0

        return {
            "id": sale.id,
            "product_id": sale.product_id,
            "product_name": product_name,
            "quantity": sale.quantity,
            "sale_price": sale_price,
            "total_sale_price": sale.total_sale,
            "total_cost": sale.total_cost,
            "extra_cost": sale.extra_cost or 0,
            "net_profit": net_profit,
            "date": sale.sale_date.strftime("%Y/%m/%d") if sale.sale_date else "",
            "sale_date": sale.sale_date,
        }
    except Exception as e:
        print(f"Error in sale_to_dict: {e}")
        return None


def products_to_dict_list(products: list) -> list:
    """تبدیل لیست Product models به لیست dictionaries"""
    return [product_to_dict(p) for p in products if p]


def sales_to_dict_list(sales: list) -> list:
    """تبدیل لیست Sale models به لیست dictionaries"""
    return [sale_to_dict(s) for s in sales if s]
