"""
ولیدیشن‌های حذف محصول و فروش
"""

from ..repository import ProductRepository, SaleRepository, RepositoryManager
from ..repository.converters import product_to_dict, sale_to_dict


class DeletionValidator:
    """ولیدیشن عملیات حذف"""

    def __init__(
        self, product_repo: ProductRepository = None, sale_repo: SaleRepository = None
    ):
        """
        Args:
            product_repo: ProductRepository instance (اختیاری)
            sale_repo: SaleRepository instance (اختیاری)
        """
        if product_repo is None or sale_repo is None:
            repo_manager = RepositoryManager()
            self.product_repo = product_repo or repo_manager.product_repo
            self.sale_repo = sale_repo or repo_manager.sale_repo
            self._owns_repo = True
            self._repo_manager = repo_manager
        else:
            self.product_repo = product_repo
            self.sale_repo = sale_repo
            self._owns_repo = False
            self._repo_manager = None

    def __del__(self):
        """بستن repository در صورت نیاز"""
        if self._owns_repo and self._repo_manager:
            self._repo_manager.close()

    def validate_product_deletion(self, product_id: int) -> dict:
        """
        ولیدیشن حذف محصول

        Args:
            product_id: شناسه محصول

        Returns:
            دیکشنری شامل: is_valid (bool), product (dict|None)
        """
        product_model = self.product_repo.get_by_id(product_id)
        product = product_to_dict(product_model) if product_model else None

        return {"is_valid": product is not None, "product": product}

    def validate_sale_deletion(self, sale_id: int) -> dict:
        """
        ولیدیشن حذف فروش

        Args:
            sale_id: شناسه فروش

        Returns:
            دیکشنری شامل: is_valid (bool), sale (dict|None)
        """
        sale_model = self.sale_repo.get_by_id(sale_id)
        sale = sale_to_dict(sale_model) if sale_model else None

        return {"is_valid": sale is not None, "sale": sale}
