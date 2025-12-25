"""
Repository برای مدیریت عملیات دیتابیس فروش‌ها
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from ..models.sale_model import Sale


class SaleRepository:
    """Repository برای عملیات CRUD فروش‌ها"""

    def __init__(self, db: Session):
        """
        Args:
            db: Session دیتابیس SQLAlchemy
        """
        self.db = db

    def create(
        self,
        product_id: int,
        quantity: int,
        total_sale: float,
        total_cost: float,
        extra_cost: float = 0.0,
    ) -> Sale:
        """
        ایجاد فروش جدید

        Args:
            product_id: شناسه محصول
            quantity: تعداد فروخته شده
            total_sale: مبلغ کل فروش
            total_cost: مبلغ کل خرید
            extra_cost: هزینه‌های جانبی

        Returns:
            Sale: فروش ایجاد شده
        """
        sale = Sale(
            product_id=product_id,
            quantity=quantity,
            total_sale=total_sale,
            total_cost=total_cost,
            extra_cost=extra_cost,
        )
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        """
        دریافت فروش با شناسه

        Args:
            sale_id: شناسه فروش

        Returns:
            Sale یا None
        """
        try:
            return self.db.query(Sale).options(joinedload(Sale.product)).filter(Sale.id == sale_id).first()
        except Exception:
            self.db.rollback()
            return None

    def get_all(self, order_by_date: bool = True) -> List[Sale]:
        """
        دریافت تمام فروش‌ها

        Args:
            order_by_date: مرتب‌سازی بر اساس تاریخ (از جدید به قدیم)

        Returns:
            لیست فروش‌ها
        """
        query = self.db.query(Sale).options(joinedload(Sale.product))
        if order_by_date:
            query = query.order_by(desc(Sale.sale_date))
        return query.all()

    def update(
        self,
        sale_id: int,
        product_id: int = None,
        quantity: int = None,
        total_sale: float = None,
        total_cost: float = None,
        extra_cost: float = None,
    ) -> bool:
        """
        به‌روزرسانی فروش

        Args:
            sale_id: شناسه فروش
            product_id: شناسه محصول جدید (اختیاری)
            quantity: تعداد جدید (اختیاری)
            total_sale: مبلغ فروش جدید (اختیاری)
            total_cost: مبلغ خرید جدید (اختیاری)
            extra_cost: هزینه جانبی جدید (اختیاری)

        Returns:
            True اگر موفق باشد
        """
        try:
            sale = self.get_by_id(sale_id)
            if not sale:
                return False

            # فقط اگر مقدار None نباشد، به‌روزرسانی کن
            if product_id is not None:
                sale.product_id = product_id
            if quantity is not None:
                sale.quantity = quantity
            if total_sale is not None:
                sale.total_sale = total_sale
            if total_cost is not None:
                sale.total_cost = total_cost
            if extra_cost is not None:
                sale.extra_cost = extra_cost

            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def delete(self, sale_id: int) -> bool:
        """
        حذف فروش

        Args:
            sale_id: شناسه فروش

        Returns:
            True اگر موفق باشد
        """
        sale = self.get_by_id(sale_id)
        if sale:
            self.db.delete(sale)
            self.db.commit()
            return True
        return False

