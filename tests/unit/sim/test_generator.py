from fipy.ngsi.entity import BaseEntity
from fipy.sim.generator import *
import pytest


def test_float_attr_close_to():
    base = 42
    got = float_attr_close_to(base)

    assert abs(base - got.value) <= 1


def test_text_attr_from_one_of():
    choices = ['a', 'b', 'cd']
    got = text_attr_from_one_of(choices)

    assert got.value in choices


def test_bool_attr():
    got = {bool_attr().value for _ in range(100)}
    assert len(got) == 2


class Bot(BaseEntity):
    type = 'Bot'
    name: TextAttr = TextAttr.new('foobie')


def mk_bot() -> Bot:
    return Bot(id='')



@pytest.mark.parametrize('max_nid, nid', [
    (1, 2),  (1, 1), (1, -2), (2, 3),  (2, 2), (2, -3)
])
def test_nid_factory_error_if_nid_out_of_bounds(max_nid, nid):
    factory = EntityFactory.with_numeric_suffixes(max_nid, mk_bot)
    with pytest.raises(IndexError):
        factory.new_entity(nid)

@pytest.mark.parametrize('max_nid, nid', [
    (1, 0),  (2, 0), (2, 1), (3, 0),  (3, 1), (3, 2)
])
def test_nid_factory_entity_id(max_nid, nid):
    factory = EntityFactory.with_numeric_suffixes(max_nid, mk_bot)
    entity = factory.new_entity(nid)

    assert entity.id == factory.entity_id(nid)


@pytest.mark.parametrize('max_nid', [1, 2, 3])
def test_nid_factory_new_batch(max_nid):
    factory = EntityFactory.with_numeric_suffixes(max_nid, mk_bot)
    name = factory.new_entity(0).name  # NOTE name attr is constant
    want = [(factory.entity_id(nid), name) for nid in range(0, max_nid)]
    got = [(b.id, b.name) for b in factory.new_batch()]

    assert want == got


@pytest.mark.parametrize('max_nid', [1, 2, 3])
def test_entity_nid_batch(max_nid):
    factory = EntityFactory.with_numeric_suffixes(max_nid, mk_bot)
    batches = [batch for _, batch in zip(range(2), entity_batch(factory))]

    assert batches[0] == batches[1]
    # NOTE. All batches must contain the same entities b/c the name field
    # is constant.


def test_uuid_factory():
    factory = EntityFactory.with_uuid_suffixes(100, mk_bot)
    ids = {e.id for e in factory.new_batch()}

    assert len(ids) == 100
