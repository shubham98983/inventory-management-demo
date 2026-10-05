"""Shared behaviour for dataclass based models."""
from dataclasses import asdict, fields


class BaseModel:
    """Mixin that adds row mapping and dict conversion to dataclasses."""

    @classmethod
    def from_row(cls, row):
        """Build a model from a sqlite3.Row, ignoring unknown columns."""
        if row is None:
            return None
        names = {f.name for f in fields(cls)}
        return cls(**{key: row[key] for key in row.keys() if key in names})

    def to_dict(self):
        return asdict(self)
