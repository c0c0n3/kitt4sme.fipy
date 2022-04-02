import pytest

from fipy.ngsi.quantumleap import from_entity_summaries


@pytest.mark.parametrize('summaries', [
    [], [{}], [{}, {'x': 1}], [{'x': 1}, {'entityId': 'e:1'}],
    [{'entityId': 'e:1'}, {'entityType': 'Bot'}]
])
def test_return_empty_if_no_valid_entity_in_summaries(summaries):
    got = from_entity_summaries(summaries)

    assert got is not None
    assert len(got) == 0


@pytest.mark.parametrize('summaries', [
    [{'entityId': 'no:1'}, {'entityId': 'yes:2', 'entityType': 'Bot'}],
    [{'entityType': 'Bot'}, {'entityId': 'yes:2', 'entityType': 'Bot'}]
])
def test_filter_out_invalid_entity_in_summaries(summaries):
    got = from_entity_summaries(summaries)

    assert got is not None
    assert len(got) == 1
    assert got[0].id == 'yes:2'


def test_many_entities():
    summaries = [
        {'entityId': 'e:1', 'entityType': 'Bot'},
        {'entityId': 'e:2', 'entityType': 'Drone'}
    ]
    got = from_entity_summaries(summaries)

    assert len(got) == 2
    assert got[0].id == 'e:1'
    assert got[0].type == 'Bot'
    assert got[1].id == 'e:2'
    assert got[1].type == 'Drone'