from typing import Optional, List

from bitmake import ApiClient


class BitMakeApiClient(ApiClient):

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None,
                 api_secret: Optional[str] = None) -> None:
        if base_url is None:
            base_url = "https://api.bitmake.com"
        super(BitMakeApiClient, self).__init__(base_url, api_key, api_secret)

    def get_base_info(self) -> dict:
        return self._get('/t/v1/info')

    def get_symbols(self) -> List[dict]:
        return self._get('/u/v1/base/symbols')

    def get_market_index(self, symbol: Optional[str] = None) -> List[dict]:
        return self._get('/t/v1/quote/index', params={'symbol': symbol})

    def get_market_depth(self, symbol: str, scale: Optional[int] = None, level: Optional[int] = None) -> List[dict]:
        params = {
            'symbol': symbol,
            'dumpScale': scale,
            'depthLevel': level
        }
        return self._get('/t/v1/quote/depth', params=params)

    def get_market_kline(self, symbol: str, interval: str, limit: Optional[int] = None,
                         to: Optional[int] = None) -> List[dict]:
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit,
            'to': to
        }
        return self._get('/t/v1/quote/klines', params=params)

    def get_market_trades(self, symbol: str, limit: Optional[int] = None) -> List[dict]:
        return self._get('/t/v1/quote/trades', params={'symbol': symbol, 'limit': limit})

    def get_market_ticker(self, symbol: Optional[str] = None) -> List[dict]:
        return self._get('/t/v1/quote/ticker', params={'symbol': symbol})

    def get_balance(self) -> List[dict]:
        return self._get('/f/v1/account/balance', sign=True)

    def get_margin_info(self, symbol: str) -> dict:
        return self._get('/f/v1/account/margininfo', params={'symbol': symbol}, sign=True)

    def set_leverage(self, symbol: str, leverage: int):
        return self._post('/f/v1/account/leverage', params={'symbol': symbol, 'leverage': leverage}, sign=True)

    def get_futures_positions(self, symbol: Optional[str] = None) -> List[dict]:
        return self._get('/f/v1/account/futures_positions', params={'symbol': symbol}, sign=True)

    def create_order(self, symbol: str, client_order_id: str,
                     price: str, quantity: str, order_side: str,
                     order_type: str, time_in_force: str,
                     trigger_more_price: Optional[str] = None,
                     trigger_less_price: Optional[str] = None,
                     execute_more_price: Optional[str] = None,
                     execute_less_price: Optional[str] = None) -> dict:
        params = {
            'symbol': symbol,
            'clientOrderId': client_order_id,
            'price': price,
            'quantity': quantity,
            'orderSide': order_side,
            'orderType': order_type,
            'timeInForce': time_in_force,
            'triggerMorePrice': trigger_more_price,
            'triggerLessPrice': trigger_less_price,
            'executeMorePrice': execute_more_price,
            'executeLessPrice': execute_less_price,
        }
        return self._post('/f/v1/order', params=params)

    def cancel_order(self, client_order_id: Optional[str] = None, order_id: Optional[int] = None) -> dict:
        return self._delete('/f/v1/order', params={'clientOrderId': client_order_id, 'orderId': order_id})

    def batch_cancel_order(self, orders: List[dict]) -> List[dict]:
        params = []
        for order in orders:
            params.append({
                'clientOrderId': order['client_order_id'],
                'orderId': order['order_id'],
            })
        return self._post('/f/v1/order/batch_cancel', params=params)

    def get_open_orders(self, symbol: Optional[str] = None, order_side: Optional[str] = None,
                        order_type: Optional[str] = None, from_id: Optional[int] = None,
                        limit: Optional[int] = None) -> List[dict]:
        params = {
            'symbol': symbol,
            'orderSide': order_side,
            'orderType': order_type,
            'fromId': from_id,
            'limit': limit
        }
        return self._get('/f/v1/openOrders', params=params, sign=True)

    def get_history_orders(self, symbol: Optional[str] = None, order_side: Optional[str] = None,
                           order_type: Optional[str] = None, from_index: Optional[int] = None,
                           limit: Optional[int] = None) -> List[dict]:
        params = {
            'symbol': symbol,
            'orderSide': order_side,
            'orderType': order_type,
            'fromIndex': from_index,
            'limit': limit
        }
        return self._get('/f/v1/historyOrders', params=params, sign=True)

    def get_order(self, client_order_id: Optional[str] = None, order_id: Optional[int] = None):
        return self._get('/f/v1/order', params={'clientOrderId': client_order_id, 'orderId': order_id}, sign=True)

    def get_trades(self, symbol: Optional[str] = None, order_side: Optional[str] = None,
                   open_close: Optional[str] = None, match_type: Optional[str] = None,
                   from_id: Optional[int] = None, limit: Optional[int] = None) -> List[dict]:
        params = {
            'symbol': symbol,
            'orderSide': order_side,
            'openClose': open_close,
            'matchType': match_type,
            'fromId': from_id,
            'limit': limit
        }
        return self._get('/f/v1/trades', params=params, sign=True)
