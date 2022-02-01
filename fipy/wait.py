import time
from typing import Callable

from fipy.ngsi.orion import OrionClient
from fipy.ngsi.quantumleap import QuantumLeapClient


def wait_until(action: Callable[[], bool], max_wait: float = 20.0,
               sleep_interval: float = 1.0):
    """Run `action` every `sleep_interval` seconds until either `action`
    returns `True` (for stop) or `max_wait` seconds have elapsed but
    raise an assert error after waiting for longer than `wait_seconds`.
    """
    time_left_to_wait = max_wait
    while time_left_to_wait > 0:
        stop = action()
        if stop:
            return

        time_left_to_wait -= sleep_interval
        time.sleep(sleep_interval)

    assert False, f"waited longer than {max_wait} secs for {action}!"


def wait_for_orion(client: OrionClient,
                   max_wait: float = 10.0,
                   sleep_interval: float = 0.5):
    def can_list_entities():
        try:
            client.list_entities()
            return True
        except BaseException:
            return False

    wait_until(can_list_entities, max_wait, sleep_interval)


def wait_for_quantumleap(client: QuantumLeapClient,
                         max_wait: float = 10.0,
                         sleep_interval: float = 0.5):
    def can_list_entities():
        try:
            client.list_entities()
            return True
        except BaseException as e:
            return False

    wait_until(can_list_entities, max_wait, sleep_interval)
