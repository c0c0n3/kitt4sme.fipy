import pytest

from fipy.dict import *


class MyKey(KeyValue[str, int]):

    def __init__(self, value: int):
        super().__init__('my-key', value)


def test_read_sets_value():
    kv = MyKey(1)
    d = {kv.key(): 2}
    v = kv.read(d)

    assert v == 2
    assert kv.value() == 2


def test_can_add_key_with_none_value():
    kv = KeyValue('k')
    assert kv.value() is None

    d = {}
    kv.add(d)
    assert d[kv.key()] is None


def test_add_to_dict_can_create_fresh_dict():
    kv1 = MyKey(1)
    kv2 = KeyValue('x', 2)
    d = add_to_dict(kv1, kv2)

    assert d is not None
    assert d[kv1.key()] == kv1.value()
    assert d[kv2.key()] == kv2.value()


def test_add_to_dict_with_input_dict():
    d = {'y': 3}
    kv1 = MyKey(1)
    kv2 = KeyValue('x', 2)
    d = add_to_dict(kv1, kv2, data=d)

    assert d is not None
    assert d[kv1.key()] == kv1.value()
    assert d[kv2.key()] == kv2.value()
    assert d['y'] == 3


def test_merge_dict_no_inputs():
    d = merge_dicts()
    assert d == {}


def test_merge_dict_latter_keys_override_previous():
    d1 = { 'x': 1, 'y': 2 }
    d2 = { 'y': 3 }
    r = merge_dicts(d1, d2)

    assert r == { 'x': 1, 'y': 3 }


@pytest.mark.parametrize('inputs, expected', [
    ([{'x': 1}], {'x': 1}),
    ([{'x': 1}, {'y': 1}, {'z': 1}], {'x': 1, 'y': 1, 'z': 1})
])
def test_merge_dict(inputs, expected):
    r = merge_dicts(*inputs)
    assert r == expected
