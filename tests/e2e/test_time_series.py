import pytest

from fipy.ngsi.orion import OrionClient
from fipy.ngsi.quantumleap import QuantumLeapClient
from fipy.wait import wait_until
from tests.util.fiware import BotSampler, SubMan


BOT_N = 2
SAMPLES_PER_BOT = 3
BOT_ENTITY_TYPE = 'Bot'
SPEED_ATTR_NAME = 'speed'


def upload_bot_entities(orion: OrionClient):
    sampler = BotSampler(pool_size=BOT_N, orion=orion)
    sampler.sample(samples_n=SAMPLES_PER_BOT, sampling_rate=1.5)


def bot_entity_id(nid: int) -> str:
    sampler = BotSampler(pool_size=BOT_N)
    return sampler.entity_id(nid)


def has_time_series(quantumleap: QuantumLeapClient) -> bool:
    size = quantumleap.count_data_points(BOT_ENTITY_TYPE, SPEED_ATTR_NAME)
    return size > (SAMPLES_PER_BOT * BOT_N) / 2  # (*)
# NOTE. Orion missed notifications. If things happen too fast, Orion might
# not notify QL of all Bot entities it got from the sampler.
# If memory serves, by default, if Orion gets multiple updates for the
# same entity within one second, it'll only notify subscribers of the
# latest update.


@pytest.fixture(scope='module')
def upload_entities(orion: OrionClient, quantumleap: QuantumLeapClient):
    SubMan().create_subscriptions()
    upload_bot_entities(orion)
    wait_until(lambda: has_time_series(quantumleap))


def test_bot_series(upload_entities, quantumleap: QuantumLeapClient):
    entity_series = quantumleap.entity_series(
        entity_id=bot_entity_id(1), entity_type=BOT_ENTITY_TYPE,
        entries_from_latest=SAMPLES_PER_BOT
    )
    r = entity_series.dict()

    assert r[SPEED_ATTR_NAME]
    assert len(r[SPEED_ATTR_NAME]) > 0


def test_bot_type_series(upload_entities, quantumleap: QuantumLeapClient):
    entity_series_dict = quantumleap.entity_type_series(
        entity_type=BOT_ENTITY_TYPE
    )

    assert len(entity_series_dict) == BOT_N
    for k in entity_series_dict:
        r = entity_series_dict[k].dict()

        assert r[SPEED_ATTR_NAME]
        assert len(r[SPEED_ATTR_NAME]) > 0
