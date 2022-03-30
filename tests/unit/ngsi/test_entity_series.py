from datetime import datetime
import pandas as pd
import pytest
from typing import List

from fipy.ngsi.entity import EntitySeries


raw_tix = ["2022-03-28T18:03:18.923+00:00", "2022-03-28T18:03:20.458+00:00",
           "2022-03-28T18:03:22.011+00:00"]
tix = [datetime.fromisoformat(t) for t in raw_tix]
directions = ["S", "N", "N"]
speeds = [1.308673138, 1.935175709, 1.451720504]

def mk_entity_query_result(extra_attrs=[]):
    return {
        "entityId": "urn:ngsi-ld:Bot:2",
        "entityType": "Bot",
        "index": raw_tix,
        "attributes": extra_attrs + [
            {
                "attrName": "direction",
                "values": directions
            },
            {
            "attrName": "speed",
            "values": speeds
            }
        ]
    }


def test_dynamic_model_fields():
    r = EntitySeries.from_quantumleap_format(mk_entity_query_result())

    assert r.index == tix
    assert r.direction == directions
    assert r.speed == speeds


def test_convert_to_data_frame_like():
    r = EntitySeries.from_quantumleap_format(mk_entity_query_result())

    assert r.dict() == {
        'index': tix,
        'direction': directions,
        'speed': speeds
    }


def test_error_on_none_input():
    with pytest.raises(AttributeError):
        EntitySeries.from_quantumleap_format(None)


def test_empty_series_on_missing_result_fields():
    r = EntitySeries.from_quantumleap_format({})
    assert r.dict() == { 'index': [] }


@pytest.mark.parametrize('attr_dicts', [
    [{'attrName': ''}], [{'values': [1, 2, 3]}],
    [{'attrName': ''}, {'values': [1, 2, 3]}]
])
def test_skip_incomplete_attr_payloads(attr_dicts):
    entity_query_result = mk_entity_query_result(extra_attrs=attr_dicts)
    r = EntitySeries.from_quantumleap_format(entity_query_result)

    assert r.dict() == {
        'index': tix,
        'direction': directions,
        'speed': speeds
    }


def test_convert_quantumleap_data_to_pandas():
    r = EntitySeries.from_quantumleap_format(mk_entity_query_result())
    time_indexed_df = pd.DataFrame(r.dict()).set_index('index')

    delta = time_indexed_df.index.max() - time_indexed_df.index.min()
    assert delta.seconds == 3
    assert delta.microseconds == 88000

    direction_column_values = time_indexed_df['direction'].to_list()
    assert direction_column_values == directions

    max_speed = time_indexed_df['speed'].max()
    assert max_speed == max(speeds)


class ESeries(EntitySeries):
    e_attr: List[int]


def test_convert_custom_entity_series_to_pandas():
    r = ESeries(index=tix, e_attr=[1, 2, 3])
    time_indexed_df = pd.DataFrame(r.dict()).set_index('index')

    delta = time_indexed_df.index.max() - time_indexed_df.index.min()
    assert delta.seconds == 3
    assert delta.microseconds == 88000

    e_attrs_column_values = time_indexed_df['e_attr'].to_list()
    assert e_attrs_column_values == [1, 2, 3]
