"""
Repository برای مدیریت عملیات دیتابیس محصولات
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.product_model import Product


class ProductRepository:
    """Repository برای عملیات CRUD محصولات"""

    def __init__(self, db: Session):
        """
        Args:
            db: Session دیتابیس SQLAlchemy
        """
        self.db = db

    def create(self, name: str, stock: int) -> tuple[Product, bool]:
        """
        ایجاد محصول جدید

        Args:
            name: نام محصول
            stock: موجودی اولیه

        Returns:
            tuple: (Product, is_created) - is_created True اگر محصول جدید باشد
        """
        try:
            # چک کن که محصول قبلاً وجود داره یا نه
            existing_product = self.get_by_name(name)
            if existing_product:
                return existing_product, False
            
            product = Product(name=name, stock=stock)
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            return product, True
        except Exception:
            self.db.rollback()
            raise

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        دریافت محصول با شناسه

        Args:
            product_id: شناسه محصول

        Returns:
            Product یا None
        """
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_name(self, name: str) -> Optional[Product]:
        """
        دریافت محصول با نام

        Args:
            name: نام محصول

        Returns:
            Product یا None
        """
        return self.db.query(Product).filter(Product.name == name).first()

    def get_all(self) -> List[Product]:
        """
        دریافت تمام محصولات

        Returns:
            لیست محصولات
        """
        return self.db.query(Product).all()

    def get_available_products(self) -> List[Product]:
        """
        دریافت محصولات با موجودی بیشتر از صفر

        Returns:
            لیست محصولات با موجودی
        """
        return self.db.query(Product).filter(Product.stock > 0).all()

    def update_name(self, product_id: int, new_name: str) -> bool:
        """
        به‌روزرسانی نام محصول

        Args:
            product_id: شناسه محصول
            new_name: نام جدید

        Returns:
            True اگر موفق باشد
        """
        product = self.get_by_id(product_id)
        if product:
            product.name = new_name
            self.db.commit()
            return True
        return False

    def update_stock(self, product_id: int, new_stock: int) -> bool:
        """
        به‌روزرسانی موجودی محصول

        Args:
            product_id: شناسه محصول
            new_stock: موجودی جدید

        Returns:
            True اگر موفق باشد
        """
        product = self.get_by_id(product_id)
        if product:
            product.stock = new_stock
            self.db.commit()
            return True
        return False

    def reduce_stock(self, product_id: int, quantity: int) -> bool:
        """
        کم کردن موجودی محصول

        Args:
            product_id: شناسه محصول
            quantity: مقدار کم شونده

        Returns:
            True اگر موفق باشد
        """
        product = self.get_by_id(product_id)
        if product and product.stock >= quantity:
            product.stock -= quantity
            self.db.commit()
            return True
        return False

    def increase_stock(self, product_id: int, quantity: int) -> bool:
        """
        اضافه کردن به موجودی محصول

        Args:
            product_id: شناسه محصول
            quantity: مقدار اضافه شونده

        Returns:
            True اگر موفق باشد
        """
        product = self.get_by_id(product_id)
        if product:
            product.stock += quantity
            self.db.commit()
            return True
        return False

    def delete(self, product_id: int) -> bool:
        """
        حذف محصول

        Args:
            product_id: شناسه محصول

        Returns:
            True اگر موفق باشد
        """
        try:
            product = self.get_by_id(product_id)
            if product:
                self.db.delete(product)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            raise

    def check_stock_availability(self, product_id: int, required_quantity: int) -> bool:
        """
        بررسی موجودی کافی بودن

        Args:
            product_id: شناسه محصول
            required_quantity: مقدار مورد نیاز

        Returns:
            True اگر موجودی کافی باشد
        """
        product = self.get_by_id(product_id)
        return product is not None and product.stock >= required_quantity


