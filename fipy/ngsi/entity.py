"""
Basic NGSI v2 data types.
"""

from pydantic import BaseModel
from typing import Any, List, Optional, Type


def ld_urn(unique_suffix: str) -> str:
    return f"urn:ngsi-ld:{unique_suffix}"


class Attr(BaseModel):
    type: Optional[str]
    value: Any

    @classmethod
    def new(cls, value: Any) -> Optional['Attr']:
        if value is None:
            return None
        return cls(value=value)


class FloatAttr(Attr):
    type = 'Number'
    value: float


class TextAttr(Attr):
    type = 'Text'
    value: str


class BaseEntity(BaseModel):
    id: str
    type: str

    def set_id_with_type_prefix(self, unique_suffix: str):
        own_id = f"{self.type}:{unique_suffix}"
        self.id = ld_urn(own_id)
        return self

    def to_json(self) -> str:
        return self.json(exclude_none=True)

    @classmethod
    def from_raw(cls, raw_entity: dict) -> Optional['BaseEntity']:
        own_type = cls(id='').type
        etype = raw_entity.get('type', '')
        if own_type != etype:
            return None
        return cls(**raw_entity)


class EntityUpdateNotification(BaseModel):
    data: List[dict]

    def filter_entities(self, entity_class: Type[BaseEntity]) \
            -> List[BaseEntity]:
        candidates = [entity_class.from_raw(d) for d in self.data]
        return [c for c in candidates if c is not None]


class EntitiesUpsert(BaseModel):
    actionType = 'append'
    entities: List[BaseEntity]
