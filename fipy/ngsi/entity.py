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

>>> raw_kv_bot_data = {
...     "id": ld_urn("Bot:3"), "type": "Bot", "speed": 12.3,
...     "other": "not in class def, ignore"
... }
>>> bot3 = BotEntity.from_raw_kv(raw_kv_bot_data)
>>> print(bot3)
id='urn:ngsi-ld:Bot:3' type='Bot' speed=FloatAttr(type='Number', value=12.3)

>>> raw_kv_drone_data = {
...     "id": ld_urn("Drone:4"), "type": "Drone",
...     "position": "41.40338, 2.17403"
... }
>>> drone4 = from_raw_kv_to_dyn_entity(raw_kv_drone_data)
>>> print(drone4)
id='urn:ngsi-ld:Drone:4' type='Drone' \
    position=TextAttr(type='Text', value='41.40338, 2.17403')
>>> type(drone4)  # Pydantic model dynamically created for us under the bonnet
<class 'pydantic.main.Drone'>
>>> issubclass(type(drone4), BaseEntity)
True


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
import json
from pydantic import BaseModel, create_model
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from fipy.dict import merge_dicts


NGSI_ID_FIELD = 'id'
"""The name of the NGSI ID field."""
NGSI_TYPE_FIELD = 'type'
"""The name of the NGSI type field."""


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


class ArrayAttr(Attr):
    type = 'Array'
    value: List


class StructuredValueAttr(Attr):
    type = 'StructuredValue'
    value: Dict


def json_val_to_attr(jval: Any) -> Optional[Attr]:
    """Convert a JSON value to an NGSI attribute.

    Conversion is pretty basic:
      - `int` or `float` ==> `FloatAttr`
      - `bool` ==> `BoolAttr`
      - `str` ==> `TextAttr`
      - `list` ==> `ArrayAttr`
      - `dict` ==> `StructuredValueAttr`
      - anything else ==> `None`

    Notice JSON only has float but the Python parser converts numbers without
    a fractional part to `int` which is why we map `int` to `FloatAttr`. Also
    JSON null, which the parser converts to `None`, can't be mapped to any
    attribute because there's no deterministic way to choose a corresponding
    NGSI type for it.

    Args:
        jval: a JSON value parsed by the `json` package.

    Returns:
        The corresponding NGSI attribute or `None` if the value was a JSON
        null or you pass in a value whose type is not in the above conversion
        map.
    """
    ctor_map = {
        int: FloatAttr.new,
        float: FloatAttr.new,
        bool: BoolAttr.new,
        str: TextAttr.new,
        list: ArrayAttr.new,
        dict: StructuredValueAttr.new
    }
    try:
        return ctor_map[type(jval)](jval)
    except KeyError:
        return None


JsonLike = Union[None, int, float, bool, str, list, dict]
"""The type of an NGSI entity attribute value in a JSON document.
"""

KVEntity = Dict[str, JsonLike]
"""A key-value pair representation of an NGSI entity.

A key-value pair representation is a dictionary containing:
  - 'id' key with a string value---the NGSI entity's ID.
  - 'type' key with a string value---the NGSI entity's type.
  - any number of additional key-value pairs where each value has one
    of the following types: `int`, `float`, `bool`, `str`, `list`, or
    `dict`.

Example.
>>> bot_entity = {'id': 'urn:ngsi-ld:Bot:2', 'type': 'Bot', 'speed': 12.3}
"""

EntityDict = Dict
"""A dictionary representation of an NGSI entity.

An entity dictionary is a dictionary containing:
  - 'id' key with a string value---the NGSI entity's ID.
  - 'type' key with a string value---the NGSI entity's type.
  - any number of additional key-value pairs each representing an NGSI
    attribute. That is each value `v` is a dict holding a 'value' and,
    optionally, a 'type' key. `v['type']` is a string denoting the NGSI
    attribute's type where `v['value']` is its actual value payload which
    can have any type.

Example.
>>> bot_entity = {
        'id': 'urn:ngsi-ld:Bot:2', 'type': 'Bot', \
        'speed': {'value': 12.3} \
    }
"""


def entity_kv_to_entity_dict(repr: KVEntity) -> EntityDict:
    """Convert a key-value pair representation of an NGSI entity to an
    entity dictionary.

    This function takes a key-value pair representation (ignoring extra
    key-value pairs not in the above format) and converts it into an entity
    dictionary.

    Args:
        repr: key-value pair representation of the NGSI entity.

    Returns:
        The corresponding entity dictionary representation. Notice any
        input key-value pair `(k, v)` where `v` is `None` or is not
        `JsonLike` gets ignored. This means the returned dict won't
        have a key `k` in it.
    """
    fields = {
        NGSI_ID_FIELD: repr.get(NGSI_ID_FIELD, ''),
        NGSI_TYPE_FIELD: repr.get(NGSI_TYPE_FIELD, '')
    }
    for (k, v) in repr.items():
        if k != NGSI_ID_FIELD and k != NGSI_TYPE_FIELD:
            f = json_val_to_attr(v)
            if f is not None:
                fields[k] = json_val_to_attr(v)
    return fields


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
    def _has_same_ngsi_type(cls, raw_entity: dict) -> bool:
        own_type = cls(id='').type
        etype = raw_entity.get(NGSI_TYPE_FIELD, '')

        return (own_type == etype)

    @classmethod
    def from_raw(cls, raw_entity: EntityDict) -> Optional['BaseEntity']:
        """Instantiate a `BaseEntity` subclass from its entity dictionary
        representation.

        Args:
            raw_entity: a dictionary containing an NGSI ID and type field
                plus any number of attribute fields. ID and type have a
                string value whereas an attribute field value is a dict
                containing a 'value' key to look up the attribute's value
                and optionally a 'type' key to look up the attribute's type.

        Returns:
            `None` if the `raw_entity['type']` is not the same as that of
            the `BaseEntity` subclass you called this method from. Otherwise
            an instance of the subclass at hand populated with the ID and
            attributes found in the input dict. Notice we only extract attr
            values for those attributes you declared in the subclass and we
            ignore everything else contained in `raw_entity`.
        """
        if cls._has_same_ngsi_type(raw_entity):
            return cls(**raw_entity)
        return None

    @classmethod
    def from_raw_kv(cls, raw_entity: KVEntity) -> Optional['BaseEntity']:
        """Instantiate a `BaseEntity` subclass from its entity key-value
        pair representation.

        Args:
            raw_entity: a dictionary containing an NGSI ID and type field
                plus any number of value fields. ID and type have a string
                value whereas a value field has a value of type: `int`,
                `float`, `bool`, `str`, `list`, or `dict`.

        Returns:
           `None` if the `raw_entity['type']` is not the same as that of
            the `BaseEntity` subclass you called this method from. Otherwise
            an instance of the subclass at hand populated with the ID and
            attributes found in the input dict. Notice we only extract field
            values for those attributes you declared in the subclass and we
            ignore everything else contained in `raw_entity`.
        """
        if not cls._has_same_ngsi_type(raw_entity):
            return None

        fields = entity_kv_to_entity_dict(raw_entity)
        return cls(**fields)


Entity = TypeVar('Entity', bound=BaseEntity)
"""The generic type of NGSI entities. An NGSI entity type is a subclass
of `BaseEntity`.
"""


def from_raw_kv_to_dyn_entity(raw_entity: KVEntity) -> Entity:
    """Create a `BaseEntity` subclass on the fly to hold the data extracted
    from the given key-value pair NGSI entity representation.

    Args:
        raw_entity: a dictionary containing an NGSI ID and type field plus
            any number of value fields. ID and type have a string value
            whereas a value field has a value of type: `int`, `float`, `bool`,
            `str`, `list`, or `dict`.

    Returns:
        An instance of a new subclass of `BaseEntity` named after the NGSI
        type in the input `raw_entity`. This instance `r` will have `id` and
        `type` fields populated from `raw_entity`. Likewise, there will be
        an `Attr` field in correspondence of every other key-value pair
        `(k, v)` in `raw_entity`. The field name will be `k` and
        `r.k.value == v`.
    """
    fields = entity_kv_to_entity_dict(raw_entity)
    model_name = fields[NGSI_TYPE_FIELD]
    dynamic_model = create_model(model_name, __base__=BaseEntity, **fields)
    return dynamic_model()  # (*) see NOTE below

# NOTE. Pydantic model.
# We create a dynamic Pydantic model to extend BaseEntity since we don't
# have a specific BaseEntity subclass to instantiate. So when creating the
# model we pass in the attribute names as field names. But we also stick in
# their values so Pydantic will use them as default values. As a result of
# that, if you access any of the attributes in the returned model instance,
# e.g. x.attr1, you'll get the corresponding value from the original raw
# entity dict.

def to_ngsi_json(raw_entity_doc: str) -> str:
    """Convert the input JSON document to NGSI-v2 JSON.

    Notice this is just a convenience function to parse the JSON, call
    `from_raw_kv_to_dyn_entity` on the parsed value and the convert the
    generated NGSI entity to JSON.

    Args:
        raw_entity_doc: a JSON document containing an object which should
            be key-value pair representation of an NGSI entity.

    Returns:
        NGSI-v2 JSON encoding the data in the input document.
    """
    raw_entity = json.loads(raw_entity_doc)
    entity = from_raw_kv_to_dyn_entity(raw_entity)
    return entity.to_json()


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