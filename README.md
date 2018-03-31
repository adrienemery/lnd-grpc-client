# lnd-grpc-client
A python grpc client for LND (Lightning Network Daemon) ⚡⚡⚡

This is a wrapper around the default grpc interface that handles setting up credentials (including macaroons). An async client is also available to do fun async stuff like listening for invoices in the background. 

Because of async support this only works with python 3.5+.

## Installation
```bash
$ pip install lndgrpc
```

## How to use
The api mirrors the underlying lnd grpc api (http://api.lightning.community/) but methods will be in pep8 style. ie. `.GetInfo()` becomes `.get_info()`.

```python
from lndgrpc import LNDClient

# pass in the ip-address with RPC port
lnd = LNDClient("127.0.0.1:10009")

lnd.get_info()

print('Listening for invoices...')
for invoice in lnd.subscribe_invoices():
    print(invoice)
```

### Async

```python
import asyncio
from lndgrpc import AsyncLNDClient

# pass in the ip-address with RPC port
async_lnd = AsyncLNDClient("127.0.0.1:10009")

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

