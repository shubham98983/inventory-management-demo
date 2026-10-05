from dataclasses import dataclass

from app.models.base import BaseModel


@dataclass
class Category(BaseModel):
    id: int
    name: str
    description: str = ""
