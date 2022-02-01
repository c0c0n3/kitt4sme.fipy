from pydantic import BaseModel
from typing import List, Optional, Type

from fipy.http.header import HttpHeader


class FiwareServiceHeader(HttpHeader):

    def __init__(self, value: Optional[str] = None):
        super().__init__(value)

    def canonical_name(self) -> str:
        return 'fiware-service'


class FiwareServicePathHeader(HttpHeader):

    def __init__(self, value: Optional[str] = None):
        super().__init__(value)

    def canonical_name(self) -> str:
        return 'fiware-servicepath'


class FiwareCorrelatorHeader(HttpHeader):

    def __init__(self, value: Optional[str] = None):
        super().__init__(value)

    def canonical_name(self) -> str:
        return 'fiware-correlator'


class FiwareContext(BaseModel):
    service: Optional[str]
    service_path: Optional[str]
    correlator: Optional[str]

    @staticmethod
    def _to_header(fiware_header_cls: Type[HttpHeader],
                   value: str) -> Optional[HttpHeader]:
        if value:
            return fiware_header_cls(value)
        return None

    def service_header(self) -> Optional[FiwareServiceHeader]:
        return self._to_header(FiwareServiceHeader, self.service)

    def service_path_header(self) -> Optional[FiwareServicePathHeader]:
        return self._to_header(FiwareServicePathHeader, self.service_path)

    def correlator_header(self) -> Optional[FiwareCorrelatorHeader]:
        return self._to_header(FiwareCorrelatorHeader, self.correlator)

    def headers(self) -> List[HttpHeader]:
        hs = [self.service_header(), self.service_path_header(),
              self.correlator_header()]
        return [h for h in hs if h]
