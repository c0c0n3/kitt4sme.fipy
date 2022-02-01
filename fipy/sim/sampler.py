from abc import ABC, abstractmethod
import time

from fipy.ngsi.entity import BaseEntity
from fipy.ngsi.orion import OrionClient


class DevicePoolSampler(ABC):
    """Simulate collecting readings from a pool of devices and sending them
    to Orion.

    Subclasses implement `new_device_entity` to assemble device readings
    into an NGSI entity.
    """

    def __init__(self, pool_size: int, orion: OrionClient):
        """Create a new instance.

        Args
            pool_size: How many devices the pool should simulate.
            orion: A client to connect to Orion.
        """
        self._device_n = pool_size
        self._orion = orion

    @abstractmethod
    def new_device_entity(self) -> BaseEntity:
        """Create a new NGSI entity containing device data to send to
        Orion."""
        pass

    def _ensure_nid_bounds(self, nid: int):
        assert 0 < nid <= self._device_n

    def make_device_entity(self, nid: int) -> BaseEntity:
        self._ensure_nid_bounds(nid)
        entity = self.new_device_entity()
        entity.set_id_with_type_prefix(f"{nid}")
        return entity

    def entity_id(self, nid: int) -> str:
        return self.make_device_entity(nid).id

    def send_device_readings(self, nid: int) -> BaseEntity:
        data = self.make_device_entity(nid)
        self._orion.upsert_entity(data)
        return data

    def sample(self, samples_n: int, sampling_rate: float):
        """Send `sample_n` batches of readings to Orion every `sampling_rate`
        seconds.

        Each batch contains an NGSI entity for each device in the pool.
        """
        for _ in range(samples_n):
            xs = [self.make_device_entity(nid)
                  for nid in range(1, self._device_n + 1)]
            self._orion.upsert_entities(xs)

            time.sleep(sampling_rate)
