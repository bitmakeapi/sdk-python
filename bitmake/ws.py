import asyncio
import gzip
import json
import logging
import time
import urllib.parse
from enum import Enum
from json import JSONDecodeError
from typing import Optional

import websockets
from websockets.exceptions import ConnectionClosed

from bitmake import ApiClient, BitMakeException


class PushDataType(Enum):

    ACCOUNT_ORDER = 'Order'
    ACCOUNT_ORDER_UPDATE = 'OrderUpdate'
    ACCOUNT_BALANCE = 'Balance'
    ACCOUNT_BALANCE_UPDATE = 'BalanceUpdate'
    ACCOUNT_FUTURES_POSITION = 'FuturesPosition'
    ACCOUNT_FUTURES_POSITION_UPDATE = 'FuturesPositionUpdate'
    ACCOUNT_TRADE_UPDATE = 'TradeUpdate'

    MARKET_TRADE = 'trade'
    MARKET_REALTIME = 'realtimes'
    MARKET_KLINE = 'kline'
    MARKET_INDEX = 'index'
    MARKET_DEPTH = 'diffMergedDepth'
    MARKET_BOOK_TICKER = 'bookTicker'

    @classmethod
    def from_event_or_topic(cls, event_or_topic: str):
        for member in cls.__members__.values():
            if event_or_topic == member.value:
                return cls[member.name]
        return None


class RespDataType(Enum):

    MARKET_TRADE = 'trade'
    MARKET_REALTIME = 'realtimes'
    MARKET_KLINE = 'kline'
    MARKET_INDEX = 'index'
    MARKET_DEPTH = 'diffMergedDepth'
    MARKET_BOOK_TICKER = 'bookTicker'

    @classmethod
    def from_topic(cls, topic: str):
        for member in cls.__members__.values():
            if topic == member.value:
                return cls[member.name]
        return None


class PushData(object):

    def __init__(self, data_type: PushDataType, data: [dict, list], is_first: bool):
        self.data_type = data_type
        self.data = data
        self.is_first = is_first

    def __str__(self):
        return "PushData{{data_type: {0}, data: {1}}}".format(self.data_type, self.data)


class RespData(object):

    def __init__(self, data_type: RespDataType, data: dict):
        self.data_type = data_type
        self.data = data

    def __str__(self):
        return "RespData{{data_type: {0}, data: {1}}}".format(self.data_type, self.data)


class BitMakeWebsocketApiClient(ApiClient):

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None,
                 api_secret: Optional[str] = None, binary: Optional[bool] = None):
        if base_url is None:
            base_url = "wss://ws.bitmake.com/t/v1/ws"
        super(BitMakeWebsocketApiClient, self).__init__(base_url, api_key, api_secret)

        self._binary = binary
        self._ws: websockets.WebSocketClientProtocol[None] = None
        self._last_ping_time = None
        self._last_active_time = None
        self._queue = asyncio.Queue(maxsize=1024)
        self._log = logging.getLogger('bitmake.BitMakeWebsocketApiClient')

    async def connect(self) -> None:
        ws_url = self._base_url
        if isinstance(self._binary, bool):
            ws_url = ws_url + '?' + 'binary=' + (self._binary and 'true' or 'false')

        headers = None
        if self._api_key and self._api_secret:
            ts = self._current_timestamp()
            p = urllib.parse.urlsplit(ws_url)
            signature_payload = self._get_signature_payload(ts, 'GET', p.path, p.query)
            sign = self._sign(signature_payload)

            headers = {
                'FM-API-KEY': self._api_key,
                'FM-API-TIMESTAMP': ts,
                'FM-API-SIGN': sign
            }

        self._ws = await websockets.connect(uri=ws_url, extra_headers=headers, ping_interval=None)
        self._log.debug("websocket connected.")
        asyncio.create_task(self._keepalive_ping())
        asyncio.create_task(self._loop_handle_message())

    async def disconnect(self) -> None:
        if self._ws and self._ws.open:
            await self._ws.close()
            self._ws = None

    async def subscribe(self, topic: str, params: Optional[dict] = None):
        message = dict()
        message['e'] = 'sub'
        message['tp'] = topic
        if params:
            message['ps'] = params
        return await self.send_message(message)

    async def unsubscribe(self, topic):
        return await self.send_message({'e': 'cancel', 'tp': topic})

    @property
    def connected(self) -> bool:
        return self._ws and self._ws.open

    async def recv(self):
        if not self.connected:
            return None
        return await self._queue.get()

    async def recv_data(self) -> [PushData, RespData]:
        data = await self.recv()
        assert isinstance(data, dict)

        if 'co' in data:
            resp_data_type = RespDataType.from_topic(data['tp'])
            if resp_data_type is None:
                raise BitMakeException(-100, "invalid response data:" + str(data))
            return RespData(resp_data_type, {'co': data['co'], 'm': data['m']})
        else:
            push_data_type = PushDataType.from_event_or_topic(data['e'])
            if push_data_type is not None:
                # this is account data push
                is_first = 'Update' not in push_data_type.value
                return PushData(push_data_type, data['d'], is_first)
            elif 'tp' in data:
                push_data_type = PushDataType.from_event_or_topic(data['tp'])
                if push_data_type is not None:
                    return PushData(push_data_type, data['d'], data['f'])
        raise BitMakeException(-101, "invalid push data:" + str(data))

    async def _keepalive_ping(self) -> None:
        await asyncio.sleep(1)
        while self.connected:
            try:
                now = int(time.time() * 1000)
                if not self._last_ping_time or now - self._last_ping_time > 60000:
                    self._last_ping_time = now
                    await self.send_message({"ping": now})
            except ConnectionClosed:
                self._log.info("websocket connection has closed.")
                return
            await asyncio.sleep(10)

    async def _loop_handle_message(self):
        while self.connected:
            try:
                msg = await self._ws.recv()
                msg_json = self._parse_recv_msg(msg)
                if msg_json:
                    self._on_message(msg_json)
            except ConnectionClosed:
                self._ws = None
                self._log.info("websocket connection closed.")
                return
            except RuntimeError:
                self._log.exception("recv runtime error.")

    def _on_message(self, msg) -> None:
        if not msg:
            return

        if isinstance(msg, dict) and 'pong' in msg:
            self._last_active_time = self._current_timestamp()
            self._log.debug("websocket recv last pong time: %s", self._last_active_time)
            return
        else:
            self._queue.put_nowait(msg)

    async def send_message(self, msg):
        data = json.dumps(msg)
        self._log.debug("send message: %s", data)
        await self._ws.send(data)

    def _parse_recv_msg(self, msg: [str, bytes]) -> [str, None]:
        try:
            if isinstance(msg, bytes):
                data = gzip.decompress(msg).decode()
            else:
                data = msg

            if data == 'ping':
                # ignore server ping message
                self._log.debug("receive server ping message. reply pong frame")
                self._ws.pong(b'pong')
                return None
            else:
                return json.loads(data)
        except gzip.BadGzipFile:
            self._log.exception("decompress error")
            return None
        except JSONDecodeError:
            self._log.exception("parse json error")
            return None
