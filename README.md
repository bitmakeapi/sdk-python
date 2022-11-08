# BitMake Python3 SDK 

This is BitMake Official Python3 SDK

## Installation

```
pip3 install bitmake
```

## Rest Example

```python
from bitmake.rest import BitMakeApiClient

api_client = BitMakeApiClient(api_key='TestApiKey', api_secret='TestSecret')
order_response = api_client.create_order('BTC_USD', 'client_order_123', '10000', '0.01', 'BUY', 'LIMIT', 'GTC')
print(order_response)
```

## Websocket Example
### Public Channels

```python
from bitmake.ws import BitMakeWebsocketApiClient, RespData, PushData

ws_client = BitMakeWebsocketApiClient()
await ws_client.connect()
await ws_client.subscribe('diffMergedDepth', {'symbol': 'BTC_USD'}) # subscribe `diffMergedDepth` topic
await ws_client.subscribe('trade', {'symbol': 'BTC_USD'}) # subscribe `trade` topic
while ws_client.connected:
    data = await ws_client.recv_data()
    assert isinstance(data, RespData) or isinstance(data, PushData)
    if isinstance(data, RespData):
        # received response data
        # for example: RespData{data_type: RespDataType.MARKET_DEPTH, data: {'co': 0, 'm': 'success'}}
        print("recv resp data type: {} data: {}".format(data.data_type, data.data))
    elif isinstance(data, PushData):
        # received push data
        # for example: PushData{data_type: PushDataType.MARKET_DEPTH, data: [{'s': 'BTC_USD', 't': 1667874854633, 'vs': 527579119, 've': 527579128, 'b': [['20636', '0.1336'], ['20634', '0.1402']], 'a': [['20649', '0.06'], ['20654', '0.0727']]}]}
        print("recv push data type: {} data: {}".format(data.data_type, data.data))
```

### Private Channels

```python
from bitmake.ws import BitMakeWebsocketApiClient, RespData, PushData

ws_client = BitMakeWebsocketApiClient(api_key='TestApiKey', api_secret='TestSecret')
await ws_client.connect()
# Optionally you can subscribe any public topic
# await ws_client.subscribe('diffMergedDepth', {'symbol': 'BTC_USD'}) # subscribe `diffMergedDepth` topic
# await ws_client.subscribe('trade', {'symbol': 'BTC_USD'}) # subscribe `trade` topic
while ws_client.connected:
    data = await ws_client.recv_data()
    assert isinstance(data, RespData) or isinstance(data, PushData)
    if isinstance(data, RespData):
        # received response data
        # for example: RespData{data_type: RespDataType.MARKET_DEPTH, data: {'co': 0, 'm': 'success'}}
        print("recv resp data type: {} data: {}".format(data.data_type, data.data))
    elif isinstance(data, PushData):
        # received push data
        # for example: PushData{data_type: PushDataType.ACCOUNT_BALANCE, data: [{'token': 'USDT', 'available': '40', 'total': '40'}]}
        print("recv push data type: {} data: {}".format(data.data_type, data.data))
```