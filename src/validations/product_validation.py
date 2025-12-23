"""
ولیدیشن‌های محصول
"""

from ..repository import ProductRepository, RepositoryManager
from ..repository.converters import product_to_dict


class ProductValidator:
    """ولیدیشن عملیات محصول"""

    def __init__(self, product_repo: ProductRepository = None):
        """
        Args:
            product_repo: ProductRepository instance (اختیاری)
        """
        if product_repo is None:
            repo_manager = RepositoryManager()
            self.product_repo = repo_manager.product_repo
            self._owns_repo = True
            self._repo_manager = repo_manager
        else:
            self.product_repo = product_repo
            self._owns_repo = False
            self._repo_manager = None

    def __del__(self):
        """بستن repository در صورت نیاز"""
        if self._owns_repo and self._repo_manager:
            self._repo_manager.close()

    def validate_product_exists(self, product_id: int) -> dict:
        """
        ولیدیشن وجود محصول

        Args:
            product_id: شناسه محصول

        Returns:
            دیکشنری شامل: is_valid (bool), product (dict|None)
        """
        product_model = self.product_repo.get_by_id(product_id)
        product = product_to_dict(product_model) if product_model else None

        return {
            'is_valid': product is not None,
            'product': product
        }

    def validate_product_name(self, name: str) -> dict:
        """
        ولیدیشن نام محصول

        Args:
            name: نام محصول

        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None), name (str|None)
        """
        if not name or not name.strip():
            return {
                'is_valid': False,
                'error_message': '❌ نام نمی‌تواند خالی باشد.'
            }

        name_str = name.strip()

        # بررسی طول نام (حداقل 2، حداکثر 155 کاراکتر)
        if len(name_str) < 2:
            return {
                'is_valid': False,
                'error_message': '❌ نام باید حداقل 2 کاراکتر باشد.'
            }

        if len(name_str) > 155:
            return {
                'is_valid': False,
                'error_message': '❌ نام نمی‌تواند بیش از 155 کاراکتر باشد.'
            }

        return {
            'is_valid': True,
            'error_message': None,
            'name': name_str
        }

    def validate_product_quantity(self, quantity: int) -> dict:
        """
        ولیدیشن موجودی محصول

        Args:
            quantity: موجودی

        Returns:
            دیکشنری شامل: is_valid (bool), error_message (str|None), quantity (int|None)
        """
        try:
            qty = int(quantity)
            if qty < 0:
                raise ValueError("موجودی نمی‌تواند منفی باشد")

            # بررسی حد معقول (حداکثر 1 میلیون)
            if qty > 1_000_000:
                raise ValueError("موجودی بیش از حد است")

        except (ValueError, TypeError):
            return {
                'is_valid': False,
                'error_message': '❌ لطفاً عدد صحیح و مثبت وارد کنید.'
            }

        return {
            'is_valid': True,
            'error_message': None,
            'quantity': qty
        }
