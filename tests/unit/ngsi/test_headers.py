import pytest

from fipy.ngsi.headers import *


@pytest.mark.parametrize('svc, path, cor, want', [
    (None, None, None, set()),
    ('s', None, None, {FiwareServiceHeader}),
    ('s', 'p', None, {FiwareServiceHeader, FiwareServicePathHeader}),
    ('s', None, 'c', {FiwareServiceHeader, FiwareCorrelatorHeader}),
    (None, 'p', None, {FiwareServicePathHeader}),
    (None, 'p', 'c', {FiwareServicePathHeader, FiwareCorrelatorHeader}),
    ('s', 'p', None, {FiwareServiceHeader, FiwareServicePathHeader}),
    (None, None, 'c', {FiwareCorrelatorHeader}),
    ('s', 'p', 'c', {FiwareServiceHeader, FiwareServicePathHeader,
                     FiwareCorrelatorHeader}),
])
def test_fiware_ctx_header_types(svc, path, cor, want):
    ctx = FiwareContext(service=svc, service_path=path, correlator=cor)
    got = {*[type(h) for h in ctx.headers()]}
    assert want == got


@pytest.mark.parametrize('svc, path, cor, want', [
    (None, None, None, set()),
    ('s', None, None, {'s'}),
    ('s', 'p', None, {'s', 'p'}),
    ('s', None, 'c', {'s', 'c'}),
    (None, 'p', None, {'p'}),
    (None, 'p', 'c', {'p', 'c'}),
    ('s', 'p', None, {'s', 'p'}),
    (None, None, 'c', {'c'}),
    ('s', 'p', 'c', {'s', 'p', 'c'}),
])
def test_fiware_ctx_header_values(svc, path, cor, want):
    ctx = FiwareContext(service=svc, service_path=path, correlator=cor)
    got = {*[h.value() for h in ctx.headers()]}
    assert want == got
