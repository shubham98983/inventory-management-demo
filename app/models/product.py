from dataclasses import dataclass
from typing import Optional

from app.models.base import BaseModel


@dataclass
class Product(BaseModel):
    id: int
    sku: str
    name: str
    price: float
    description: str = ""
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    cost: float = 0.0
    quantity: int = 0
    reorder_level: int = 10
    created_at: str = ""

    def stock_value(self):
        """Value of the stock on hand at cost price."""
        return round(self.cost * self.quantity, 2)

    def retail_value(self):
        """Value of the stock on hand at selling price."""
        return round(self.price * self.quantity, 2)
