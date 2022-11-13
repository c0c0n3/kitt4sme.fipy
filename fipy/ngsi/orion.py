"""
Wrapper calls to Orion Context Broker.
"""

from typing import List, Optional
from uri import URI

from fipy.http.jclient import JsonClient
from fipy.ngsi.entity import BaseEntity, Entity, EntitiesUpsert
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
    """Client to interact with Orion.
    """

    def __init__(self, base_url: URI, ctx: FiwareContext):
        """Create a new client.

        Args:
            base_url: Orion's root URL, e.g. URI('http://localhost:1026').
            ctx: the FIWARE context to use. Notice the service determines
                which Orion tenant DB this client will interact with.
        """
        self._urls = OrionEndpoints(base_url)
        self._ctx = ctx
        self._http = JsonClient()

    def upsert_entity(self, data: BaseEntity):
        """Put the given entity data in Orion's context.
        If there's no entity, then insert a new one. Otherwise update the
        existing one.

        Args:
            data: entity data to put in the context.
        """
        url = self._urls.entities({'options': 'upsert'})
        self._http.post(url=url, json_payload=data.dict(),
                        headers=self._ctx.headers())


    def upsert_entities(self, data: List[BaseEntity]):
        """Same as upsert_entity but for a list of entities.

        Args:
            data: entities to put in the context.
        """
        url = self._urls.update_op()
        payload = EntitiesUpsert(entities=data)
        self._http.post(url=url, json_payload=payload.dict(),
                        headers=self._ctx.headers())

    def list_entities(self) -> List[BaseEntity]:
        """Fetch an entity summary of each entity in the context.

        Returns:
            A list of `BaseEntity`, one for each entity found in the
            context. Notice these are partial representations of the
            entities, they only have the `id` and `type` fields and
            no attributes.
        """
        url = self._urls.entities({'attrs': 'id'})  # (*)
        entity_arr = self._http.get(url=url, headers=self._ctx.headers())
        models = [BaseEntity.parse_obj(entity_dict)
                  for entity_dict in entity_arr]
        return models
    # NOTE. Include only `id` and `type` fields of each entity.
    # See: https://github.com/c0c0n3/kitt4sme.fipy/issues/12

    def list_entities_of_type(self, like: Entity) -> List[Entity]:
        """Fetch all entities of the given type.

        Args:
            like: example entity to specify the type of the entities
                to fetch.

        Returns:
            A list of entities of the requested type. Each entity holds the
            full representation with all the attributes plus the `id` and
            `type` fields.
        """
        url = self._urls.entities({'type': like.type})
        entity_arr = self._http.get(url=url, headers=self._ctx.headers())
        models = [like.from_raw(entity_dict) for entity_dict in entity_arr]
        return models

    def fetch_entity(self, like: Entity) -> Optional[Entity]:
        """Fetch the entity of the given type and ID.

        Args:
            like: example entity to specify the type and ID of the entity
                to fetch.

        Returns:
            The requested entity if it exists, `None` otherwise. The entity
            holds the full representation with all the attributes plus the
            `id` and `type` fields.
        """
        query = {'id': like.id, 'type': like.type}
        url = self._urls.entities(query)
        entity_arr = self._http.get(url=url, headers=self._ctx.headers())
        models = [like.from_raw(entity_dict) for entity_dict in entity_arr]
        return models[0] if len(models) > 0 else None

    def subscribe(self, sub: dict):
        """Create a new subscription.

        Args:
            sub: subscription data.
        """
        url = self._urls.subscriptions()
        self._http.post(url=url, json_payload=sub,
                        headers=self._ctx.headers())

    def list_subscriptions(self) -> List[dict]:
        """Fetch all the current subscriptions.

        Returns:
            A list of `dict`, each holding the data of a subscription.
        """
        url = self._urls.subscriptions()
        return self._http.get(url=url, headers=self._ctx.headers())
