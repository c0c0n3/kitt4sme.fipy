import json
from fipy.ngsi.entity import *

from tests.util.fiware import BotEntity


json_with_all_types = """
{
    "null_prop": null,
    "bool_prop": true,
    "int_prop": 1,
    "float_prop": 1.0,
    "string_prop": "yo",
    "array_prop": [1, 2],
    "object_prop": {"h": 3}
}
"""

def test_json_null_to_attr():
    parsed = json.loads(json_with_all_types)
    attr = json_val_to_attr(parsed['null_prop'])

    assert attr is None


def test_json_to_bool_attr():
    parsed = json.loads(json_with_all_types)
    attr = json_val_to_attr(parsed['bool_prop'])

    assert attr is not None
    assert type(attr) == type(BoolAttr.new(False))
    assert attr.value == True


def test_json_to_float_attr():
    parsed = json.loads(json_with_all_types)
    for attr in (json_val_to_attr(parsed['int_prop']),
                 json_val_to_attr(parsed['float_prop'])):
        assert attr is not None
        assert type(attr) == type(FloatAttr.new(0))
        assert attr.value == 1


def test_json_to_text_attr():
    parsed = json.loads(json_with_all_types)
    attr = json_val_to_attr(parsed['string_prop'])

    assert attr is not None
    assert type(attr) == type(TextAttr.new(""))
    assert attr.value == "yo"


def test_json_to_array_attr():
    parsed = json.loads(json_with_all_types)
    attr = json_val_to_attr(parsed['array_prop'])

    assert attr is not None
    assert type(attr) == type(ArrayAttr.new([]))
    assert attr.value == [1, 2]


def test_json_to_struct_attr():
    parsed = json.loads(json_with_all_types)
    attr = json_val_to_attr(parsed['object_prop'])

    assert attr is not None
    assert type(attr) == type(StructuredValueAttr.new({}))
    assert attr.value == {"h": 3}


def test_entity_from_kv_repr():
    json_rep = """
        {
            "id": "urn:ngsi-ld:Bot:1",
            "type": "Bot",
            "speed": 1.2
        }
    """
    kv_entity = json.loads(json_rep)
    entity = BotEntity.from_raw_kv(kv_entity)

    assert entity is not None
    assert type(entity) == BotEntity
    assert entity.id == kv_entity['id']
    assert entity.type == kv_entity['type']
    assert entity.speed.value == 1.2
    assert entity.speed.type == 'Number'


def test_dyn_entity_from_kv_repr():
    json_rep = """
        {
            "id": "urn:ngsi-ld:Drone:1",
            "type": "Drone",
            "position": "41.40338, 2.17403"
        }
    """
    kv_entity = json.loads(json_rep)
    entity = from_raw_kv_to_dyn_entity(kv_entity)

    assert entity is not None
    assert issubclass(type(entity), BaseEntity)
    assert entity.id == kv_entity['id']
    assert entity.type == kv_entity['type']
    assert entity.position.value == '41.40338, 2.17403'
    assert entity.position.type == 'Text'

def test_to_ngsi_json():
    json_rep = """
        {
            "id": "urn:ngsi-ld:Drone:2",
            "type": "Drone",
            "position": "41.40338, 2.17403",
            "speed": 12.3
        }
    """
    ngsi_rep = to_ngsi_json(json_rep)

    assert ngsi_rep == \
        '{"id": "urn:ngsi-ld:Drone:2", "type": "Drone",' +\
        ' "position": {"type": "Text", "value": "41.40338, 2.17403"},' +\
        ' "speed": {"type": "Number", "value": 12.3}}'
