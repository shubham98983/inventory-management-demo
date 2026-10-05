from dataclasses import dataclass

from app.models.base import BaseModel


@dataclass
class Supplier(BaseModel):
    id: int
    name: str
    contact_email: str = ""
    phone: str = ""
    address: str = ""
    created_at: str = ""
