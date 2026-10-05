from dataclasses import dataclass
from typing import Optional

from app.models.base import BaseModel


@dataclass
class StockMovement(BaseModel):
    id: int
    product_id: int
    quantity_change: int
    reason: str
    user_id: Optional[int] = None
    created_at: str = ""
