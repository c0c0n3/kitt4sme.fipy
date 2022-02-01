from typing import List
from fipy.ngsi.orion import OrionClient
from fipy.wait import wait_until
from tests.util.fiware import BotEntity, BotSampler


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


def test_bots(orion: OrionClient):
    sorted_bots = upload_bot_entities(orion)

    wait_until(lambda: has_bot_entities(orion))

    sorted_orion_bots = list_bot_entities(orion)

    assert len(sorted_bots) == len(sorted_orion_bots)
    for i in range(len(sorted_bots)):
        assert sorted_bots[i].id == sorted_orion_bots[i].id
