# lndgrpc
A python grpc client for LND (Lightning Network Daemon) ⚡⚡⚡

This is a wrapper around the default grpc interface that handles setting up credentials (including macaroons). An async client is also available to do fun async stuff like listening for invoices in the background. 

## Dependencies
- Python 3.6+
- Working LND lightning node, take note of its ip address.
- Copy your admin.macaroon and tls.cert files from your node to a directoy on your machine. 


## Installation
```bash
pip install py-lnd-grpc

# Test it is working
# Set these values as needed!
export CRED_PATH=/path/to/macaroon/and/tls/cert
export LND_NODE_IP=192.168.1.xx

# This will run a get_info() request on your node, checking its connection.
python3 -m lndgrpc
```



### Environment Variables

These environment variables are only used when testing node connectivity and/or correct module installation from the command line. This library is primarily used through Python scripting.

```bash
export CRED_PATH=/path/to/macaroon/and/tls/cert
export LND_NODE_IP=192.168.1.xx

python3 -m lndgrpc

# You should expect to see:
#
# .....
# .....
# .....
# lndgrpc package is installed... Wow it works!
```

## Basic Usage
The api mirrors the underlying lnd grpc api (http://api.lightning.community/) but methods will be in pep8 style. ie. `.GetInfo()` becomes `.get_info()`.

```python
from lndgrpc import LNDClient

# pass in the ip-address with RPC port and network ('mainnet', 'testnet', 'simnet')
# the client defaults to 127.0.0.1:10009 and mainnet if no args provided
lnd = LNDClient("127.0.0.1:10009", network='simnet')

# Unlock you wallet
lnd.unlock_wallet(wallet_password=b"your_wallet_password")

# Get general data about your node
lnd.get_info()

print('Listening for invoices...')
for invoice in lnd.subscribe_invoices():
    print(invoice)
```

### Async

```python
import asyncio
from lndgrpc import AsyncLNDClient

async_lnd = AsyncLNDClient()

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
By default the client will attempt to lookup the `readonly.macaron` and `tls.cert` files in the mainnet directory. 
However if you want to specify a different macaroon or different path you can pass in the filepath explicitly.

```python
lnd = LNDClient(
    macaroon_filepath='~/.lnd/invoice.macaroon', 
    cert_filepath='path/to/tls.cert'
)
```

## Generating LND Proto Files
```bash
virtualenv lnd
source lnd/bin/activate
pip install grpcio grpcio-tools googleapis-common-protos sh
git clone https://github.com/lightningnetwork/lnd.git
mkdir genprotos
git clone https://github.com/googleapis/googleapis.git

# python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto
```

```python
from pathlib import Path
import shutil
import sh

for proto in list(Path("../lnd/lnrpc").rglob("*.proto")):
    shutil.copy(proto, Path.cwd())

protos = list(Path(".").glob("*.proto"))

for protofile in protos:
    try:
        sh.python("-m", "grpc_tools.protoc", "--proto_path=.", "--python_out=.", "--grpc_python_out=.", str(protofile))
        protos.remove(protofile)
    except Exception as e:
        print(f"Error in proto: {protofile}")
```

Last Step:
In File: verrpc_pb2_grpc.py
Change:
import verrpc_pb2 as verrpc__pb2
To:
from lndgrpc import verrpc_pb2 as verrpc__pb2

## Deploy to Test-PyPi
```bash
poetry build
twine check dist/*
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```