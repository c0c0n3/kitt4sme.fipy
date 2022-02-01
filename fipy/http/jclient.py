from typing import List

from requests import Session, Response

from .header import HttpHeader, pack


class JsonClient:
    """Simple HTTP client to operate on resources that are expected to have
    a JSON representation.
    """

    def __init__(self, timeout=60, verify=True):
        """Create a new instance.

        Args:
            timeout: error out if the request takes longer than this.
            verify: verify SSL certificates for HTTPS connections.
        """
        self._timeout = timeout
        self._verify = verify
        self._http = Session()

    @staticmethod
    def _handle_response(r: Response) -> dict:
        r.raise_for_status()
        if r.text:
            return r.json()
        return {}

    @staticmethod
    def _prep_headers(hs: List[HttpHeader] = None) -> dict:
        if hs:
            return pack(*hs)
        return {}

    def get(self, url: str, headers: List[HttpHeader] = None) -> dict:
        """GET the JSON resource identified by `url`.

        Args:
            url: the resource identifier.
            headers: any optional headers to add to the request.

        Returns:
            the JSON representation of the resource.
        """
        response = self._http.get(url=url,
                                  headers=self._prep_headers(headers),
                                  timeout=self._timeout,
                                  verify=self._verify)
        return self._handle_response(response)

    def post(self, url: str, json_payload: dict,
             headers: List[HttpHeader] = None) -> dict:
        """POST a JSON payload.

        Args:
            url: where to post.
            json_payload: the data.
            headers: any optional headers to add to the request.
                ('Content-Type: application/json' will be added
                automatically.)

        Returns:
            JSON returned by the server if any.
        """
        response = self._http.post(url=url,
                                   headers=self._prep_headers(headers),
                                   json=json_payload,
                                   timeout=self._timeout,
                                   verify=self._verify)
        return self._handle_response(response)
    # NOTE. Content-Type header. Requests adds application/json automatically
    # when using the 'json' named argument.

    def put(self, url: str, json_payload: dict,
            headers: List[HttpHeader] = None) -> dict:
        """PUT a JSON representation of the resource identified by `url`.

        Args:
            url: the resource identifier.
            json_payload: the data.
            headers: any optional headers to add to the request.
                ('Content-Type: application/json' will be added
                automatically.)

        Returns:
            JSON returned by the server if any.
        """
        response = self._http.put(url=url,
                                  headers=self._prep_headers(headers),
                                  json=json_payload,
                                  timeout=self._timeout,
                                  verify=self._verify)
        return self._handle_response(response)
    # NOTE. Content-Type header. Requests adds application/json automatically
    # when using the 'json' named argument.

    def delete(self, url: str, headers: List[HttpHeader] = None) -> dict:
        """DELETE the resource identified by `url`.

        Args:
            url: the resource identifier.
            headers: any optional headers to add to the request.

        Returns:
            JSON returned by the server if any.
        """
        response = self._http.delete(url=url,
                                     headers=self._prep_headers(headers),
                                     timeout=self._timeout,
                                     verify=self._verify)
        return self._handle_response(response)
