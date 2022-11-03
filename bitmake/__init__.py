import hmac
import logging
import time
import urllib.parse
from typing import Optional, Any, Dict

from requests import Request, Session, Response

bitmake_logger = logging.getLogger("BitMake")


class BitMakeException(RuntimeError):

    def __init__(self, code: int, msg: str):
        self._code = code
        self._msg = msg

    def __str__(self):
        return f'code:{self._code} msg:{self._msg}'

    @property
    def code(self):
        return self._code

    @property
    def msg(self):
        return self._msg


class ApiClient(object):

    def __init__(self, base_url: str, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> None:
        self._session = Session()
        self._base_url = base_url
        self._api_key = api_key
        self._api_secret = api_secret

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None, sign: Optional[bool] = False) -> Any:
        return self._request('GET', path, params=params, sign=sign)

    def _post(self, path: str, params: Optional[Any] = None, sign: Optional[bool] = True) -> Any:
        return self._request('POST', path, json=params, sign=sign)

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None, sign: Optional[bool] = True) -> Any:
        return self._request('DELETE', path, params=params, sign=sign)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        self._log_request(method, path, **kwargs)

        sign = kwargs.pop('sign', False)
        request = Request(method, urllib.parse.urljoin(self._base_url, path), **kwargs)
        if sign is True:
            if not self._api_key or not self._api_secret:
                raise BitMakeException(-1, "You must be authenticated to use this method")
            self._sign_request(request)
        response = self._session.send(request.prepare())

        return self._process_response(response)

    @staticmethod
    def _log_request(method: str, path: str, **kwargs):
        if kwargs.get('params'):
            req_params = kwargs['params']
        elif kwargs.get('json'):
            req_params = kwargs['json']
        else:
            req_params = ""

        bitmake_logger.debug("[BitMake] request %s %s params: %s", method, path, req_params)

    def close(self):
        self._session.close()

    def _sign_request(self, request: Request) -> None:
        ts = self._current_timestamp()
        prepared = request.prepare()
        p = urllib.parse.urlsplit(request.prepare().url)
        signature_payload = self._get_signature_payload(ts, prepared.method, p.path, p.query, prepared.body)
        signature = self._sign(signature_payload)
        request.headers['FM-API-KEY'] = self._api_key
        request.headers['FM-API-SIGN'] = signature
        request.headers['FM-API-TIMESTAMP'] = str(ts)

    def _get_signature_payload(self, timestamp: int, method: str, path: str,
                               query: Optional[str] = None,
                               body: Optional[bytes] = None) -> bytes:
        payload = f'{self._api_key}{timestamp}{method}{path}'.encode()
        if query:
            payload += f'{urllib.parse.unquote(query)}'.encode()
        if body:
            payload += body
        return payload

    def _sign(self, payload: bytes) -> str:
        return hmac.new(self._api_secret.encode(), payload, 'sha256').hexdigest()

    @staticmethod
    def _current_timestamp():
        return int(time.time() * 1000)

    @staticmethod
    def _process_response(response: Response) -> Any:
        bitmake_logger.debug("[BitMake] response code: %d body: %s", response.status_code, response.content)
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if response.status_code == 200:
                return data
            elif isinstance(data, dict) and data.get("code") and data.get("msg"):
                raise BitMakeException(data["code"], data["msg"])
            else:
                raise BitMakeException(-2, "api server return http code: %d" % response.status_code)

