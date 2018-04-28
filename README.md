# lndgrpc
A python grpc client for LND (Lightning Network Daemon) ⚡⚡⚡

This is a wrapper around the default grpc interface that handles setting up credentials (including macaroons). An async client is also available to do fun async stuff like listening for invoices in the background. 

## Dependencies
Python 2.7, 3.4+
Note: the async client is only available for Python 3.5+

## Installation
```bash
$ pip install lndgrpc
```

## Basic Usage
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

### Specifying Macaroon/Cert files
By default the client will attempt to lookup the `readonly.macaron` and `tls.cert` files in thier default directory. 
However if you want to specify a different macaroon or different path you can pass in the filepath explicitly.

```python
lnd = LNDClient("127.0.0.1:10009", macaroon_filepath='~/.lnd/invoice.macaroon', cert_filepath='path/to/tls.cert')
```


### TODO
- [ ] improve docs
- [ ] add tests

