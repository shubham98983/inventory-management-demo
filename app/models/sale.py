from dataclasses import dataclass, field
from typing import List

from app.models.base import BaseModel


@dataclass
class SaleItem(BaseModel):
    id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: float
    discount_percent: float = 0.0

    def line_total(self):
        return round(self.unit_price * (1 - self.discount_percent / 100) * self.quantity, 2)


@dataclass
class Sale(BaseModel):
    id: int
    user_id: int
    subtotal: float
    tax: float
    total: float
    created_at: str = ""
    items: List[SaleItem] = field(default_factory=list)
