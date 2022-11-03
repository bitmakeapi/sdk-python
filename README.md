# BitMake Python3 SDK 

This is BitMake Official Python3 SDK

## Installation

```
pip3 install bitmake
```

## Example

```python
from bitmake.rest import BitMakeApiClient

api_client = BitMakeApiClient(api_key='TestApiKey', api_secret='TestSecret')
order_response = api_client.create_order('BTC_USD', 'client_order_123', '10000', '0.01', 'BUY', 'LIMIT', 'GTC')
print(order_response)
```