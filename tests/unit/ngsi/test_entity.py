from fipy.ngsi.entity import *

import pytest
from tests.util.fiware import BotEntity


def test_float_attr_from_value():
    f = FloatAttr.new(2.3)

    assert f.type == 'Number'
    assert f.value == 2.3


def test_text_attr_from_value():
    t = TextAttr.new('howzit')

    assert t.type == 'Text'
    assert t.value == 'howzit'


@pytest.mark.parametrize('raw', [True, False])
def test_bool_attr_from_value(raw):
    t = BoolAttr.new(raw)

    assert t.type == 'Boolean'
    assert t.value == raw


def test_ngsi_entity_from_json_ignore_unknown_attrs():
    want = BotEntity(id='1', speed=FloatAttr.new(1.2))
    got = BotEntity.parse_raw(
        '{"id": "1", "type": "Bot", "x": 3, "speed": {"value": 1.2}}')

    assert want == got


def test_build_entity_with_preformatted_id():
    bot = BotEntity(id='').set_id_with_type_prefix('1')

    assert bot.type == 'Bot'
    assert bot.id == ld_urn('Bot:1')


def test_build_entity_from_dict():
    raw_bot_data = {
        "id": ld_urn("Bot:2"),
        "speed": { "value": 12.3 }
    }
    bot = BotEntity(**raw_bot_data)

    assert bot.type == 'Bot'
    assert bot.id == 'urn:ngsi-ld:Bot:2'
    assert bot.speed.type == 'Number'
    assert bot.speed.value == 12.3


def test_serialize_entity_with_attr_to_ngsi_json():
    bot = BotEntity(id='').set_id_with_type_prefix('2')
    bot.speed = FloatAttr.new(12.3)
    got = bot.to_json()
    want = '{"id": "urn:ngsi-ld:Bot:2", "type": "Bot",' + \
           ' "speed": {"type": "Number", "value": 12.3}}'

    assert want == got


def test_filter_entities_out_of_ngsi_notification():
    notification = EntityUpdateNotification(
        data=[
            {"id": "1", "type": "Bot", "speed": {"value": 1.1}},
            {"id": "2", "type": "NotMe", "speed": {"value": 2.2}},
            {"id": "3", "type": "Bot", "speed": {"value": 3.3}}
        ]
    )
    filtered = notification.filter_entities(BotEntity)

    assert len(filtered) == 2
    assert {e.type for e in filtered} == {BotEntity(id='').type}
    assert [e.speed.value for e in filtered] == [1.1, 3.3]
