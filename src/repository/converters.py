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

    net_profit = sale.total_sale - sale.total_cost - sale.extra_cost
    sale_price = sale.total_sale / sale.quantity if sale.quantity > 0 else 0

    return {
        "id": sale.id,
        "product_id": sale.product_id,
        "product_name": sale.product.name if sale.product else "نامشخص",
        "quantity": sale.quantity,
        "sale_price": sale_price,
        "total_sale_price": sale.total_sale,
        "total_cost": sale.total_cost,
        "extra_cost": sale.extra_cost,
        "net_profit": net_profit,
        "date": sale.sale_date.strftime("%Y/%m/%d") if sale.sale_date else "",
        "sale_date": sale.sale_date,
    }


def products_to_dict_list(products: list) -> list:
    """تبدیل لیست Product models به لیست dictionaries"""
    return [product_to_dict(p) for p in products if p]


def sales_to_dict_list(sales: list) -> list:
    """تبدیل لیست Sale models به لیست dictionaries"""
    return [sale_to_dict(s) for s in sales if s]
