from dataclasses import dataclass

from app.models.base import BaseModel


@dataclass
class User(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str
    role: str = "staff"
    created_at: str = ""

    def is_admin(self):
        return self.role == "admin"

    def to_dict(self):
        data = super().to_dict()
        data.pop("password_hash", None)
        return data
