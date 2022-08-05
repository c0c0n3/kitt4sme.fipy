"""
Basic NGSI v2 data types.

Examples
--------

>>> from fipy.ngsi.entity import *


1. NGSI attributes from values.

>>> FloatAttr.new(2.3).json()
'{"type": "Number", "value": 2.3}'
>>> print(TextAttr.new('howzit'))
type='Text' value='howzit'


2. NGSI entity from JSON---ignores unknown attributes.

>>> BaseEntity.parse_raw('{"id": "1", "type": "foo", "x": 3}')
BaseEntity(id='1', type='foo')


3. Define your own entity.

>>> class BotEntity(BaseEntity):
...     type = 'Bot'
...     speed: Optional[FloatAttr]


4. Build entity with preformatted ID.

>>> bot1 = BotEntity(id='').set_id_with_type_prefix('1')
>>> bot1.id, bot1.type
('urn:ngsi-ld:Bot:1', 'Bot')


5. Don't serialise unset NGSI attributes.

>>> bot1.to_json()
'{"id": "urn:ngsi-ld:Bot:1", "type": "Bot"}'


6. Build entity from dictionary.

>>> raw_bot_data = {"id": ld_urn("Bot:2"), "speed": {"value": 12.3}}
>>> bot2 = BotEntity(**raw_bot_data)
>>> print(bot2)
id='urn:ngsi-ld:Bot:2' type='Bot' speed=FloatAttr(type='Number', value=12.3)


7. Serialise entity with attribute data to NGSI JSON.

>>> bot2.to_json()
'{"id": "urn:ngsi-ld:Bot:2", "type": "Bot", \
    "speed": {"type": "Number", "value": 12.3}}'


8. Filter non-Bot entities out of an NGSI update notification.

>>> notification = EntityUpdateNotification(
...     data=[
...         {"id": "1", "type": "Bot", "speed": {"value": 1.1}},
...         {"id": "2", "type": "NotMe", "speed": {"value": 2.2}},
...         {"id": "3", "type": "Bot", "speed": {"value": 3.3}}
...     ]
... )
>>> notification.filter_entities(BotEntity)
[BotEntity(id='1', type='Bot', speed=FloatAttr(type='Number', value=1.1)), \
 BotEntity(id='3', type='Bot', speed=FloatAttr(type='Number', value=3.3))]


10. Have a look at the EntitySeries doc for examples of how to work
with entity series.
"""

from datetime import datetime
from pydantic import BaseModel, create_model
from typing import Any, Dict, List, Optional, Type, TypeVar

from fipy.dict import merge_dicts


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


class BoolAttr(Attr):
    type = 'Boolean'
    value: bool


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


Entity = TypeVar('Entity', bound=BaseEntity)
"""The generic type of NGSI entities. An NGSI entity type is a subclass
of `BaseEntity`.
"""

class EntityUpdateNotification(BaseModel):
    data: List[dict]

    def filter_entities(self, entity_class: Type[BaseEntity]) \
            -> List[BaseEntity]:
        candidates = [entity_class.from_raw(d) for d in self.data]
        return [c for c in candidates if c is not None]


class EntitiesUpsert(BaseModel):
    actionType = 'append'
    entities: List[BaseEntity]


class EntitySeries(BaseModel):
    """Time-indexed sequence of entity attribute values.
    This class defines the index, sub-classes fill in attribute values.

    Say you've defined an entity type `E:BaseEntity` with two attributes
    very creatively named `attr1` and `attr2`. You've also captured a
    time series of `E` instances of a specific ID
    ```
        t0, e0 = { id: aw42, type: E, attr1: v0, attr2: w0 }
        t1, e1 = { id: aw42, type: E, attr1: v1, attr2: w1 }
        t2, e2 = { id: aw42, type: E, attr1: v2, attr2: w2 }
    ```
    Then you could define an `EntitySeries` subclass to reshuffle the
    above data in a more data frame friendly format. The pattern is
    ```
        index: t0, t1, t2, ...
        attr1: v0, v1, v2, ...
        attr2: w0, w1, w2, ...
    ```
    where `v0` is the value of attribute `attr1` at time `t0`, `v1` is
    the value at time `t1`, and so on.

    So you'd define a sub-class like
    ```
        class ESeries(EntitySeries):
            attr1: List[int]
            attr2: List[float]
    ```
    create an instance from the original time series
    ```
        aw42_series = ESeries(
            index=[t0, t1, t2], attr1=[v0, v1, v2], attr2=[w0, w1, w2]
        )
    ```
    and then get a data frame friendly representation by calling the
    `dict` method. For example, here's how you'd get a properly time
    indexed Pandas frame out of the `aw42_series` above:
    ```
        data = aw42_series.dict()
        time_indexed_df = pd.DataFrame(data).set_index('index')
    ```
    Have a look at the test cases for more examples.
    """
    index: List[datetime]

    @classmethod
    def from_quantumleap_format(cls, entity_query_result: dict) \
            -> 'EntitySeries':
        """Convert an entity series returned by a Quantum Leap query to an
        `EntitySeries`.

        The returned object will have a field called `index` containing the
        time index array returned by Quantum Leap. Also, it will have a field
        for each returned attribute array and the field name will be the same
        as the attribute name.

        Args:
            entity_query_result: a dictionary representing the JSON object
                returned by a call to the `/v2/entities/{entity ID}` Quantum
                Leap endpoint.

        Returns:
            An `EntitySeries` holding the same data as the input result set,
            but in a data frame friendly shape.
        """
        def to_kv(attr_payload: dict) -> dict:
            key = attr_payload.get('attrName', '')
            if key == '':
                return {}
            return {key: attr_payload.get('values', [])}

        attributes = entity_query_result.get('attributes', [])
        attr_fields = merge_dicts(*[to_kv(x) for x in attributes])

        raw_tix = entity_query_result.get('index', [])
        tix = [datetime.fromisoformat(t) for t in raw_tix]

        model_name = f"{entity_query_result.get('entityType', '')}Series"
        dynamic_model = create_model(model_name, __base__=cls, **attr_fields)
        return dynamic_model(index=tix)  # (*) see NOTE below

# NOTE. Pydantic default values.
# We create a dynamic Pydantic model to extend EntitySeries since we don't
# know the attribute names beforehand. So when creating the model we pass
# in the attribute names as field names. But we also stick in their values
# so Pydantic will use them as default values. As a result of that, if you
# access one of the attributes in the returned model instance, e.g. x.attr1,
# you'll get the corresponding value array returned by the Quantum Leap query.
# This is okay since the returned object is supposed to be immutable.

    @classmethod
    def from_quantumleap_type_format(cls, entity_type_query_result: dict) \
            -> Dict[str, 'EntitySeries']:
        """Convert a set of entity series returned by a Quantum Leap query
        to a dictionary of `EntitySeries`.

        The returned dictionary will have an `EntitySeries` value for each
        entity series in the query result. Each `EntitySeries` value will
        be keyed by the entity ID of the entity series it represents.

        Notice each `EntitySeries` will have a field called `index` containing
        the time index array returned by Quantum Leap. Also, it will have a
        field for each returned attribute array and the field name will be
        the same as the attribute name.

        Basically this method is just a convenience transformation which
        leverages the `from_quantumleap_format` method as the pseudo-code
        below hints
        ```
        {                              {
          "entityType": "T",    ----\    "e1_id": from_quantumleap_format(e1),
          "entities": [e1, e2,  ----/    "e2_id": from_quantumleap_format(e2),
                        ...]                   ...
        }                              }
        ```

        Args:
            entity_type_query_result: a dictionary representing the JSON
                object returned by a call to the `v2/types/{entity type}`
                Quantum Leap endpoint.

        Returns:
            An dictionary of `EntitySeries` values keyed by their respective
            entity ID.
        """
        etype = entity_type_query_result.get('entityType', '')
        entities = entity_type_query_result.get('entities', [])

        series_dict = {}
        for e in entities:
            ec = dict(e)  # (*) see NOTE below
            ec['entityType'] = etype

            id = ec.get('entityId', '')
            series = cls.from_quantumleap_format(ec)

            series_dict[id] = series

        return series_dict

# NOTE. Immutability. That's a good thing which is why we don't change
# the entity_type_query_result input dict. But from_quantumleap_format
# expects a dict w/ an entityType in it, so we make a shallow copy of
# each entity dict in entity_type_query_result to add the entity type.
# The shallow copy will work b/c we only change a top-level key so the
# change won't be reflected in the original dict. This saves us from a
# deep copy which would be way more expensive.