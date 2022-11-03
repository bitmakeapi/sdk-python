import unittest
from unittest.mock import MagicMock

from requests import Request, Response

from bitmake import ApiClient, BitMakeException


class ApiClientTests(unittest.TestCase):

    def test_sign_request(self):
        api_client = ApiClient('https://api.bitmake.com/', 'TestApiKey', 'TestSecret')
        api_client._current_timestamp = MagicMock(return_value=1666239334000)
        r = Request('GET', 'https://api.bitmake.com/f/v1/trades', params=dict(symbol='BTC_USD', limit=20))
        api_client._sign_request(r)
        self.assertEqual(r.headers['FM-API-SIGN'], "06a3b28074ab52ffdc93dd195b043eeea904ba65fefb04448b63fdd7905e5366")
        self.assertEqual(r.headers['FM-API-TIMESTAMP'], "1666239334000")
        self.assertEqual(r.headers['FM-API-KEY'], "TestApiKey")

    def test_process_response(self):
        response = Response()
        response.status_code = 200
        response._content = '{"t": 1666232097038, "s": "BTC-PERP", "i": "19058"}'.encode()
        data = ApiClient._process_response(response)
        self.assertEqual(data["t"], 1666232097038)
        self.assertEqual(data["s"], "BTC-PERP")
        self.assertEqual(data["i"], "19058")

        response.status_code = 400
        response._content = '{"code": 100089, "msg": "invalid request"}'.encode()

        with self.assertRaises(BitMakeException) as cm:
            ApiClient._process_response(response)
            self.assertEqual(cm.exception.code, 100089)
            self.assertEqual(cm.exception.msg, "invalid request")
