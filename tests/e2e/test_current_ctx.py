from typing import List
from fipy.ngsi.entity import FloatAttr
from fipy.ngsi.orion import OrionClient
from fipy.wait import wait_until
from tests.util.fiware import BotEntity, BotSampler, DroneEntity, \
    RoomEntity, RoomSampler


def upload_room_entities(orion: OrionClient) -> List[RoomEntity]:
    sampler = RoomSampler(pool_size=2, orion=orion)
    room1 = sampler.send_device_readings(1)
    room2 = sampler.send_device_readings(2)

    return [room1, room2]


def room_type() -> str:
    return RoomEntity(id='', temperature=FloatAttr.new(0)).type


def upload_bot_entities(orion: OrionClient) -> List[BotEntity]:
    sampler = BotSampler(pool_size=2, orion=orion)
    bot1 = sampler.send_device_readings(1)
    bot2 = sampler.send_device_readings(2)

    return [bot1, bot2]


def list_bot_entities(orion: OrionClient) -> List[BotEntity]:
    like = BotEntity(id='')
    es = orion.list_entities_of_type(like)

    sorted_estimates = sorted(es, key=lambda e: e.id)
    return sorted_estimates


def has_bot_entities(orion: OrionClient) -> bool:
    es = list_bot_entities(orion)
    return len(es) > 0


def assert_bot_entity(want: BotEntity, got: BotEntity):
    assert want.id == got.id
    assert abs(want.speed.value - got.speed.value) < 0.01
    assert want.direction.value == want.direction.value


def test_bots(orion: OrionClient):
    sorted_bots = upload_bot_entities(orion)

    wait_until(lambda: has_bot_entities(orion))

    sorted_orion_bots = list_bot_entities(orion)

    assert len(sorted_bots) == len(sorted_orion_bots)
    for i in range(len(sorted_bots)):
        assert_bot_entity(want=sorted_bots[i], got=sorted_orion_bots[i])
        orion_bot = orion.fetch_entity(sorted_bots[i])
        assert_bot_entity(want=sorted_bots[i], got=orion_bot)

    summaries = orion.list_entities()
    assert len(summaries) == 2


def test_no_entities(orion: OrionClient):
    like = DroneEntity(id='1', height=FloatAttr.new(0))

    got = orion.list_entities(type=like.type)
    assert len(got) == 0

    got = orion.list_entities_of_type(like)
    assert len(got) == 0

    got = orion.fetch_entity(like)
    assert got is None


def test_rooms(orion: OrionClient):
    rooms = upload_room_entities(orion)
    want_ids = {r.id for r in rooms}

    orion_ids = orion.list_entity_ids(type=room_type())
    got_ids = {*orion_ids}

    assert want_ids == got_ids
