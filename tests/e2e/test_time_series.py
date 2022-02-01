from fipy.ngsi.orion import OrionClient
from fipy.wait import wait_until
from tests.util.fiware import BotSampler, QuantumLeapClient, SubMan


BOT_N = 2
SAMPLES_PER_BOT = 3
BOT_ENTITY_TYPE = 'Bot'
SPEED_ATTR_NAME = 'speed'


def upload_bot_entities(orion: OrionClient):
    sampler = BotSampler(pool_size=BOT_N, orion=orion)
    sampler.sample(samples_n=SAMPLES_PER_BOT, sampling_rate=1.5)


def has_time_series(quantumleap: QuantumLeapClient) -> bool:
    size = quantumleap.count_data_points(BOT_ENTITY_TYPE, SPEED_ATTR_NAME)
    return size > (SAMPLES_PER_BOT * BOT_N) / 2  # (*)
# NOTE. Orion missed notifications. If things happen too fast, Orion might
# not notify QL of all Bot entities it got from the sampler.
# If memory serves, by default, if Orion gets multiple updates for the
# same entity within one second, it'll only notify subscribers of the
# latest update.


def test_bot_series(orion: OrionClient, quantumleap: QuantumLeapClient):
    SubMan().create_subscriptions()
    upload_bot_entities(orion)
    wait_until(lambda: has_time_series(quantumleap))
