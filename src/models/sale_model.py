from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    
    # foreign key to product - SET NULL وقتی محصول حذف شود
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    product = relationship("Product", back_populates="sales")

    quantity = Column(Integer, nullable=False)
    total_sale = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    extra_cost = Column(Float, default=0.0)
    sale_date = Column(DateTime, default=datetime.utcnow)
