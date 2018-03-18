# lnd-grpc-client
A python grpc client for LND (Lightning Network Daemon) ⚡⚡⚡

This is a wrapper around the default grpc interface that handles setting up credentials (including macaroons). An async client is also available to do fun async stuff like listening for invoices in the background. 


## dependencies
- grpcio
- aiogrpc
- grpcio-tools
- googleapis-common-protos


## Installation
For now you can clone this repo or copy the three files (`rpc_pb2.py` `rpc_pb2_grpc.py`, `client.py`) into your project. I am hoping to have on PyPI soon though so its easy to integrate into a standard workflow.


## How to use
```python
from client import RPCClient

# pass in the ip-address with RPC port
lnd = RPCClient("127.0.0.1:10009")

lnd.get_info()

print('Listening for invoices...')
for invoice in lnd.subscribe_invoices():
    print(invoice)
```

### Async

```python
import asyncio
from client import AsyncRPCClient

# pass in the ip-address with RPC port
async_lnd = AsyncRPCClient("127.0.0.1:10009")

async def subscribe_invoices():
    print('Listening for invoices...')
    async for invoice in async_lnd.subscribe_invoices():
        print(invoice)

async def get_info():
    while True:
        info = await async_lnd.get_info()
        print(info)
        await asyncio.sleep(5)

async def run():
    coros = [subscribe_invoices(), get_info()]
    await asyncio.gather(*coros)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
```


### TODO
- [ ] improve docs
- [ ] add tests
