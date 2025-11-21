"""
Dependency injection و مدیریت Session دیتابیس
"""

from sqlalchemy.orm import Session
from ..db.database import SessionLocal
from .product_repository import ProductRepository
from .sale_repository import SaleRepository


def get_db() -> Session:
    """
    دریافت Session دیتابیس

    Yields:
        Session: نمونه Session دیتابیس
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_product_repository(db: Session = None) -> ProductRepository:
    """
    دریافت ProductRepository

    Args:
        db: Session دیتابیس (اختیاری)

    Returns:
        ProductRepository
    """
    if db is None:
        db = SessionLocal()
    return ProductRepository(db)


def get_sale_repository(db: Session = None) -> SaleRepository:
    """
    دریافت SaleRepository

    Args:
        db: Session دیتابیس (اختیاری)

    Returns:
        SaleRepository
    """
    if db is None:
        db = SessionLocal()
    return SaleRepository(db)


class RepositoryManager:
    """
    مدیریت کننده Repository ها با Session مشترک
    """

    def __init__(self):
        self.db = SessionLocal()
        self.product_repo = ProductRepository(self.db)
        self.sale_repo = SaleRepository(self.db)

    def close(self):
        """بستن Session"""
        self.db.close()

    def commit(self):
        """Commit تغییرات"""
        self.db.commit()

    def rollback(self):
        """Rollback تغییرات"""
        self.db.rollback()

    def __enter__(self):
        """استفاده به عنوان Context Manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """بستن Session در خروج از Context"""
        if exc_type is not None:
            self.rollback()
        self.close()
