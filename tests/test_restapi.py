import decimal
import logging
import time
import unittest
from typing import Optional

from bitmake import BitMakeException
from bitmake.rest import BitMakeApiClient
from tests import is_number

logging.basicConfig(format='[%(asctime)s] [%(levelname)5s]: %(message)s', level=logging.DEBUG)

TEST_API_KEY = ""  # set your real api key
TEST_API_SECRET = ""  # set your real api secret
TEST_BASE_URL = ""  # set your real websocket url such as 'https://api.bitmake.com/'

TEST_SPOT_SYMBOL = "BTC_USD"  # set real spot symbol name
TEST_FUTURES_SYMBOL = "BTC-USD"  # set real futures symbol name
TEST_INVALID_SYMBOL = "TEST_SYMBOL"


@unittest.skipIf(not TEST_BASE_URL, '')
class BitMakeApiClientTests(unittest.TestCase):

    def setUp(self) -> None:
        self.api_client = BitMakeApiClient(TEST_BASE_URL, TEST_API_KEY, TEST_API_SECRET)

    def tearDown(self) -> None:
        self.api_client.close()

    def test_get_base_info(self) -> None:
        data = self.api_client.get_base_info()
        self.assertTrue(isinstance(data["serverTime"], int))
        self.assertTrue(isinstance(data["clientIp"], str))

    def test_get_symbols(self) -> None:
        data = self.api_client.get_symbols()
        self.assertTrue(isinstance(data, list))

    def test_get_market_index(self) -> None:
        data = self.api_client.get_market_index(TEST_FUTURES_SYMBOL)
        self.assertTrue(len(data) == 1)
        self.assertTrue(isinstance(data[0]['t'], int))
        self.assertEqual(data[0]['s'], TEST_FUTURES_SYMBOL)
        self.assertTrue(isinstance(data[0]['i'], str))

        data = self.api_client.get_market_index()
        self.assertTrue(len(data) >= 1)

    def test_get_market_depth(self) -> None:
        data = self.api_client.get_market_depth(TEST_SPOT_SYMBOL)
        self.assertTrue(isinstance(data, list))
        self.assertTrue(data[0]['s'], TEST_SPOT_SYMBOL)
        self.assertTrue(isinstance(data[0]['t'], int))
        self.assertTrue(isinstance(data[0]['vs'], int))
        self.assertTrue(isinstance(data[0]['ve'], int))
        self.assertTrue(isinstance(data[0]['b'], list))
        self.assertTrue(isinstance(data[0]['a'], list))

    def test_get_market_kline(self) -> None:
        data = self.api_client.get_market_kline(TEST_SPOT_SYMBOL, interval='15m', limit=10)
        self.assertTrue(len(data) <= 10)
        for kline in data:
            self.assertEqual(kline['s'], TEST_SPOT_SYMBOL)
            self.assertTrue(kline['t'] % (15 * 60000) == 0)
            self.assertTrue(is_number(kline['o']))
            self.assertTrue(is_number(kline['c']))
            self.assertTrue(is_number(kline['h']))
            self.assertTrue(is_number(kline['l']))
            self.assertTrue(is_number(kline['v']))
            self.assertTrue(is_number(kline['qv']))

    def test_get_market_trades(self) -> None:
        data = self.api_client.get_market_trades(TEST_SPOT_SYMBOL, 10)
        self.assertTrue(len(data) <= 10)
        for trade in data:
            self.assertTrue(isinstance(trade['t'], int))
            self.assertTrue(is_number(trade['p']))
            self.assertTrue(is_number(trade['q']))
            self.assertTrue(isinstance(trade['m'], bool))

    def test_get_market_ticker(self) -> None:
        data = self.api_client.get_market_ticker(TEST_SPOT_SYMBOL)
        for ticker in data:
            self.assertTrue(is_number(ticker['h']))
            self.assertTrue(is_number(ticker['l']))
            self.assertTrue(is_number(ticker['o']))
            self.assertTrue(is_number(ticker['c']))
            self.assertTrue(is_number(ticker['v']))
            self.assertTrue(is_number(ticker['qv']))
            self.assertTrue(is_number(ticker['m']))

    def test_get_api_key(self) -> None:
        data = self.api_client.get_api_key()
        self.assertTrue(isinstance(data['name'], str))
        self.assertTrue(isinstance(data['userId'], int))
        self.assertTrue(isinstance(data['parentUserId'], int))
        self.assertTrue(isinstance(data['accountId'], int))
        self.assertTrue(isinstance(data['ipWhiteList'], str))

    def test_get_balance(self) -> None:
        data = self.api_client.get_balance()
        self.assertTrue(isinstance(data, list))
        for balance in data:
            self.assertTrue(isinstance(balance['token'], str))
            self.assertTrue(is_number(balance['available']))
            self.assertTrue(is_number(balance['total']))

    def test_get_margin_info(self) -> None:
        data = self.api_client.get_margin_info(TEST_SPOT_SYMBOL)
        self.assertEqual(data['symbol'], TEST_SPOT_SYMBOL)
        self.assertTrue(is_number(data['totalCollateral']))
        self.assertTrue(is_number(data['freeCollateral']))
        self.assertTrue(isinstance(data['maxLeverage'], int))
        self.assertTrue(is_number(data['marginFraction']))
        self.assertTrue(is_number(data['maintenanceMarginRequirement']))
        self.assertTrue(is_number(data['shortMax']))
        self.assertTrue(is_number(data['longMax']))
        self.assertTrue(is_number(data['longMaxNonBorrow']))
        self.assertTrue(is_number(data['baseAvailable']))
        self.assertTrue(is_number(data['quoteAvailable']))

        with self.assertRaises(BitMakeException) as cm:
            self.api_client.get_margin_info(TEST_INVALID_SYMBOL)
            self.assertTrue(cm.exception.code == 10017)
            self.assertTrue(cm.exception.msg)

    def test_create_spot_order(self) -> None:
        best_bid, best_ask = self._get_best_price(TEST_SPOT_SYMBOL)

        decimal.getcontext().prec = 2
        buy_price = '{0:f}'.format(best_bid * decimal.Decimal(0.95))
        client_order_id = f'test_{int(time.time())}'
        data = self.api_client.create_order(TEST_SPOT_SYMBOL, client_order_id, buy_price,
                                            '0.01', 'BUY', 'LIMIT', 'IOC')
        self.assertEqual(data['symbol'], TEST_SPOT_SYMBOL)
        self.assertTrue(isinstance(data['orderId'], int))
        self.assertTrue(isinstance(data['clientOrderId'], str))
        self.assertTrue(isinstance(data['createTime'], int))

    def test_cancel_order(self) -> None:
        best_bid, best_ask = self._get_best_price(TEST_SPOT_SYMBOL)

        decimal.getcontext().prec = 2
        buy_price = '{0:f}'.format(best_bid * decimal.Decimal(0.5))
        client_order_id = f'test_{int(time.time())}'
        self.api_client.create_order(TEST_SPOT_SYMBOL, client_order_id, buy_price, '0.01', 'BUY', 'LIMIT', 'GTC')
        data = self.api_client.cancel_order(client_order_id)

        self.assertTrue(isinstance(data['orderId'], int))
        self.assertTrue(data['cancelStatus'] in ('SUCCESS', 'ORDER_IN_CANCEL', 'ORDER_NOT_EXIST', 'ORDER_FILLED'))
        self.assertTrue(data['orderStatus'] in ('NEW', 'FILLED', 'CANCELLED', 'PARTIALLY_FILLED',
                                                'PENDING_CANCEL', 'REJECTED', 'PENDING_NEW'))
        self.assertTrue(is_number(data['executedQuantity']))
        self.assertTrue(is_number(data['executedAmount']))

    def test_batch_cancel_order(self) -> None:
        best_bid, best_ask = self._get_best_price(TEST_SPOT_SYMBOL)

        decimal.getcontext().prec = 2
        buy_price = '{0:f}'.format(best_bid * decimal.Decimal(0.5))

        client_order_ids = []
        for i in range(3):
            client_order_id = f'test_{int(time.time())}_{i}'
            quantity = decimal.Decimal("0.01") * (i + 1)
            self.api_client.create_order(TEST_SPOT_SYMBOL, client_order_id, buy_price,
                                         str(quantity), 'BUY', 'LIMIT', 'GTC')
            client_order_ids.append(client_order_id)

        cancel_request = []
        for client_order_id in client_order_ids:
            cancel_request.append({'client_order_id': client_order_id, 'order_id': 0})
        data = self.api_client.batch_cancel_order(cancel_request)

        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) == 3)
        for d in data:
            self.assertTrue(isinstance(d['orderId'], int))
            self.assertTrue(d['cancelStatus'] in ('SUCCESS', 'ORDER_IN_CANCEL', 'ORDER_NOT_EXIST', 'ORDER_FILLED'))

    def test_get_open_orders(self) -> None:
        data = self.api_client.get_open_orders()
        self.assertTrue(isinstance(data, list))
        for order in data:
            self._assert_order(order)

    def test_get_history_orders(self) -> None:
        data = self.api_client.get_history_orders()
        self.assertTrue(isinstance(data, list))
        for order in data:
            self._assert_order(order)

    def test_get_trades(self) -> None:
        data = self.api_client.get_trades()
        self.assertTrue(isinstance(data, list))
        for trade in data:
            self.assertTrue(isinstance(trade['tradeId'], int))
            self.assertTrue(isinstance(trade['orderId'], int))
            self.assertTrue(isinstance(trade['matchTime'], int))
            self.assertTrue(trade['matchType'] in ('NORMAL', 'LIQUIDATION', 'ADL', 'SETTLEMENT'))
            self.assertTrue(isinstance(trade['symbol'], str))
            self.assertTrue(is_number(trade['price']))
            self.assertTrue(is_number(trade['quantity']))
            self.assertTrue(is_number(trade['tradeFee']))
            self.assertTrue(isinstance(trade['tradeFeeToken'], str))
            self.assertTrue(isinstance(trade['isMaker'], bool))
            self.assertTrue(isinstance(trade['isBuyer'], bool))

    def _assert_order(self, order: dict, assert_symbol: Optional[str] = None) -> None:
        self.assertTrue(isinstance(order['clientOrderId'], str))
        self.assertTrue(isinstance(order['orderId'], int))
        self.assertTrue(isinstance(order['symbol'], str))
        if assert_symbol:
            self.assertEqual(order['symbol'], assert_symbol)
        self.assertTrue(order['orderSide'] in ('BUY', 'SELL'))
        self.assertTrue(order['orderType'] in ('LIMIT', 'MARKET', 'CONDITION_LIMIT', 'CONDITION_MARKET'))
        self.assertTrue(order['orderStatus'] in ('NEW', 'FILLED', 'CANCELLED', 'PARTIALLY_FILLED',
                                                 'PENDING_CANCEL', 'REJECTED', 'PENDING_NEW'))
        self.assertTrue(is_number(order['price']))
        self.assertTrue(is_number(order['quantity']))
        self.assertTrue(is_number(order['amount']))
        self.assertTrue(is_number(order['executedQuantity']))
        self.assertTrue(is_number(order['executedAmount']))
        if 'triggerMorePrice' in order:
            self.assertTrue(is_number(order['triggerMorePrice']))
        if 'triggerLessPrice' in order:
            self.assertTrue(is_number(order['triggerLessPrice']))
        if 'executedMorePrice' in order:
            self.assertTrue(is_number(order['executedMorePrice']))
        if 'executedLessPrice' in order:
            self.assertTrue(is_number(order['executedLessPrice']))
        self.assertTrue(isinstance(order['createTime'], int))
        self.assertTrue(isinstance(order['updateTime'], int))

    def _get_best_price(self, symbol: str) -> [decimal.Decimal, decimal.Decimal]:
        data = self.api_client.get_market_depth(symbol, level=5)
        if len(data) == 0:
            return decimal.Decimal("0"), decimal.Decimal("0")

        bids = data[0]['b']
        asks = data[0]['a']

        if len(bids) > 0:
            best_bid = decimal.Decimal(bids[0][0])
        else:
            best_bid = decimal.Decimal("0")

        if len(asks) > 0:
            best_ask = decimal.Decimal(asks[0][0])
        else:
            best_ask = decimal.Decimal("0")
        return best_bid, best_ask
