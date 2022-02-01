"""
Wrapper calls to Orion Context Broker.
"""

from typing import List, Type
from uri import URI

from fipy.http.jclient import JsonClient
from fipy.ngsi.entity import BaseEntity, EntitiesUpsert
from fipy.ngsi.headers import FiwareContext


class OrionEndpoints:

    def __init__(self, base_url: URI):
        self._base_url = base_url

    def _append(self, rel_path: str) -> URI:
        abspath = self._base_url.path / rel_path
        return self._base_url / abspath

    def entities(self, query: dict = None) -> str:
        url = self._append('v2/entities')
        if query:
            url.query = query
        return str(url)

    def update_op(self) -> str:
        url = self._append('v2/op/update')
        return str(url)

    def subscriptions(self) -> str:
        url = self._append('v2/subscriptions')
        return str(url)


class OrionClient:

    def __init__(self, base_url: URI, ctx: FiwareContext):
        self._urls = OrionEndpoints(base_url)
        self._ctx = ctx
        self._http = JsonClient()

    def upsert_entity(self, data: BaseEntity):
        url = self._urls.entities({'options': 'upsert'})
        self._http.post(url=url, json_payload=data.dict(),
                        headers=self._ctx.headers())

    def upsert_entities(self, data: List[BaseEntity]):
        url = self._urls.update_op()
        payload = EntitiesUpsert(entities=data)
        self._http.post(url=url, json_payload=payload.dict(),
                        headers=self._ctx.headers())

    def list_entities(self) -> List[BaseEntity]:
        url = self._urls.entities()
        entity_arr = self._http.get(url=url, headers=self._ctx.headers())
        models = [BaseEntity.parse_obj(entity_dict)
                  for entity_dict in entity_arr]
        return models

    def list_entities_of_type(self, like: Type[BaseEntity]) \
            -> List[BaseEntity]:
        url = self._urls.entities({'type': like.type})
        entity_arr = self._http.get(url=url, headers=self._ctx.headers())
        models = [like.parse_obj(entity_dict) for entity_dict in entity_arr]
        return models

    def subscribe(self, sub: dict):
        url = self._urls.subscriptions()
        self._http.post(url=url, json_payload=sub,
                        headers=self._ctx.headers())

    def list_subscriptions(self) -> List[dict]:
        url = self._urls.subscriptions()
        return self._http.get(url=url, headers=self._ctx.headers())
