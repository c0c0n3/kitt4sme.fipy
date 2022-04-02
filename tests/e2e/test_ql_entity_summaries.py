from fipy.ngsi.entity import BaseEntity
from fipy.ngsi.quantumleap import QuantumLeapClient
from tests.util.fiware import DroneSampler, RoomSampler
from typing import List


def upload_entities(quantumleap: QuantumLeapClient):
    drones = DroneSampler(pool_size=2)
    room = RoomSampler(pool_size=1)
    xs = [
        drones.make_device_entity(1),
        drones.make_device_entity(2),
        room.make_device_entity(1)
    ]

    quantumleap.insert_entities(xs)


def test_entity_summaries(quantumleap: QuantumLeapClient):
    upload_entities(quantumleap)

    drones = quantumleap.list_entities(entity_type='Drone')
    assert len(drones) == 2
    assert {'Drone'} == {e.type for e in drones}

    room = quantumleap.list_entities(entity_type='Room')
    assert len(room) == 1
    assert {'Room'} == {e.type for e in room}

    all_entities = quantumleap.list_entities()
    assert len(all_entities) == 3
    assert {'Room', 'Drone'} == {e.type for e in all_entities}
