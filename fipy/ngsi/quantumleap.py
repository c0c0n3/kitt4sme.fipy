"""
Wrapper calls to QuantumLeap.
"""

from datetime import datetime
from requests import HTTPError
from typing import List, Optional
from uri import URI

from fipy.http.jclient import JsonClient
from fipy.ngsi.headers import FiwareContext
from fipy.ngsi.entity import BaseEntity, EntitySeries


class QuantumLeapEndpoints:

    def __init__(self, base_url: URI):
        self._base_url = base_url

    def _append(self, rel_path: str) -> URI:
        abspath = self._base_url.path / rel_path
        return self._base_url / abspath

    def attribute(self, entity_id: str, attr_name: str,
                  query: dict = None) -> str:
        rel_path = f"v2/entities/{entity_id}/attrs/{attr_name}"
        url = self._append(rel_path)
        if query:
            url.query = query
        return str(url)

    def entity_type(self, etype: str, attr_name: str,
                    query: dict = None) -> str:
        rel_path = f"v2/types/{etype}/attrs/{attr_name}"
        url = self._append(rel_path)
        if query:
            url.query = query
        return str(url)

    def entities(self) -> str:
        url = self._append('v2/entities')
        return str(url)

    def entity_series(self, entity_id: str, entity_type: str,
                      query: dict = {}) -> str:
        rel_path = f"v2/entities/{entity_id}"
        url = self._append(rel_path)

        query['type'] = entity_type
        url.query = query

        return str(url)

    def insert_op(self) -> str:
        url = self._append('v2/notify')
        return str(url)


class QuantumLeapClient:

    def __init__(self, base_url: URI, ctx: FiwareContext):
        self._urls = QuantumLeapEndpoints(base_url)
        self._ctx = ctx
        self._http = JsonClient()

    def list_entities(self) -> List[dict]:
        try:
            url = self._urls.entities()
            return self._http.get(url=url, headers=self._ctx.headers())
        except HTTPError as e:
            if e.response.status_code == 404:
                return []
            raise e

    def insert_entities(self, data: List[BaseEntity]):
        url = self._urls.insert_op()
        payload = {
            "data": [e.dict() for e in data]
        }
        self._http.post(url=url, json_payload=payload,
                        headers=self._ctx.headers())

    def time_series(self, entity_id: str, attr_name: str,
                    query: dict = None) -> dict:
        url = self._urls.attribute(entity_id, attr_name, query)
        return self._http.get(url=url, headers=self._ctx.headers())

    def all_time_series(self, entity_type: str, attr_name: str,
                        query: dict = None) -> dict:
        url = self._urls.entity_type(entity_type, attr_name, query)
        return self._http.get(url=url, headers=self._ctx.headers())

    def count_data_points(self, entity_type: str, attr_name: str) -> int:
        try:
            series = self.all_time_series(entity_type, attr_name)
            entities = series['entities']
            sample_size = 0
            for e in entities:
                sample_size += len(e['values'])
            return sample_size
        except HTTPError:  # probably no notifications received yet...
            return 0

    def entity_series(self, entity_id: str, entity_type: str,
                      entries_from_latest: Optional[int] = None,
                      from_timepoint: Optional[datetime] = None,
                      to_timepoint: Optional[datetime] = None) -> EntitySeries:
        """Collect a sub-sequence of an entity series into data-frame like
        object.

        For each tracked entity, Quantum Leap keeps a time-indexed sequence of
        changes to that entity. You can fetch it from Quantum Leap with a
        ```
            GET /v2/entities/{entity_id}?type={entity_type}
        ```
        which is what this method does. The returned content isn't data frame
        friendly, so this method packs the returned data into an `EntitySeries`
        you can directly use with e.g. Pandas as in
        ```
            r = ql_client.entity_series('Bot:1', 'Bot')
            time_indexed_df = pd.DataFrame(r.dict()).set_index('index')
        ```

        Args:
            entity_id: The ID of the entity to retrieve.
            entity_type: The type of the entity to retrieve.
            entries_from_latest: Optional number of series entries to retrieve
                starting from the latest entry in the series. Defaults to None.
            from_timepoint: Optional datetime to retrieve all entries from the
                given timepoint. Defaults to None.
            to_timepoint: Optional datetime to retrieve all entries up to the
                given timepoint. Defaults to None.

        Returns:
            The query result packed in an `EntitySeries`.
        """
        query = {}
        if entries_from_latest:
            query['lastN'] = str(entries_from_latest)
        if from_timepoint:
            query['fromDate'] = from_timepoint.isoformat()
        if to_timepoint:
            query['toDate'] = to_timepoint.isoformat()

        url = self._urls.entity_series(entity_id, entity_type, query)
        raw_series = self._http.get(url=url, headers=self._ctx.headers())
        return EntitySeries.from_quantumleap_format(raw_series)
