import logging
import unittest

from bitmake.ws import BitMakeWebsocketApiClient


logging.basicConfig(format='[%(asctime)s] [%(levelname)5s]: %(message)s', level=logging.DEBUG)

TEST_API_KEY = ""  # set your real api key
TEST_API_SECRET = ""  # set your real api secret
TEST_WS_URL = ""  # set your real websocket url such as 'wss://ws.bitmake.com/t/v1/ws'

TEST_SPOT_SYMBOL = "BTC_USD"  # set real spot symbol name
TEST_FUTURES_SYMBOL = "BTC-USD"  # set real futures symbol name
TEST_INVALID_SYMBOL = "TEST_SYMBOL"


@unittest.skipIf(not TEST_WS_URL, '')
class BitMakeWebsocketApiClientTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.ws_client = BitMakeWebsocketApiClient(TEST_WS_URL, TEST_API_KEY, TEST_API_SECRET)
        self.log = logging.getLogger('bitmake.BitMakeWebsocketApiClientTests')
        await self.ws_client.connect()

    async def asyncTearDown(self) -> None:
        await self.ws_client.disconnect()

    async def test_subscribe(self):
        start = self.ws_client._current_timestamp()
        await self.ws_client.subscribe('diffMergedDepth', {'symbol': TEST_SPOT_SYMBOL})
        while self.ws_client.connected:
            data = await self.ws_client.recv_data()
            self.log.debug("test_subscribe recv data: %s", data)
            now = self.ws_client._current_timestamp()
            if now - start > 120000:
                break
