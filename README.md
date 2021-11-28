# lnd-grpc-client
A python grpc client for LND (Lightning Network Daemon) ⚡⚡⚡

This is a wrapper around the default grpc interface that handles setting up credentials (including macaroons). An async client is also available to do fun async stuff like listening for invoices in the background. 

## Dependencies
- Python 3.6+
- Working LND lightning node, take note of its ip address.
- Copy your admin.macaroon and tls.cert files from your node to a directory on your machine. 


## Installation
```bash
pip install lnd-grpc-client

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

### Create Example ENV File
Make a folder for holding your TLS cert and macaroons, and create a file named `node-env` which contains what is necessary to connect to your node
IN BASH
```
mkdir -p /home/you-user-name/creds/your-node-alias
cd /home/you-user-name/creds/your-node-alias
nano node-env
```

IN NANO
```
# Lightning Node Vars
export CRED_PATH=/home/you-user-name/creds/your-node-alias/lnd
export LND_NODE_IP=192.168.4.69
```

IN BASH
```
mkdir lnd
cd lnd
*copy your tls.cert and admin.macaroon in to this folder*
```

HOW TO USE
IN BASH
```
cd /home/you-user-name/creds/your-node-alias
source node-env
# THIS ADDS WHAT IS IN THE FILE AS AN ENVIRONMENT VARIABLE SO IT IS AVAILABLE WHEN YOU ARE WRITING SCRIPTS
```


## Basic Usage
The api mirrors the underlying lnd grpc api (http://api.lightning.community/) but methods will be in pep8 style. ie. `.GetInfo()` becomes `.get_info()`.

```python
import os
from pathlib import Path

from lndgrpc import LNDClient

credential_path = os.getenv("LND_CRED_PATH", None)
if credential_path == None:
	credential_path = Path.home().joinpath(".lnd")
	mac = str(credential_path.joinpath("data/chain/bitcoin/mainnet/admin.macaroon").absolute())
else:
	credential_path = Path(credential_path)
	mac = str(credential_path.joinpath("admin.macaroon").absolute())
	

node_ip = os.getenv("LND_NODE_IP")
tls = str(credential_path.joinpath("tls.cert").absolute())

lnd_ip_port = f"{node_ip}:10009"

# pass in the ip-address with RPC port and network ('mainnet', 'testnet', 'simnet')
# the client defaults to 127.0.0.1:10009 and mainnet if no args provided
lnd = LNDClient(
	lnd_ip_port,
	macaroon_filepath=mac,
	cert_filepath=tls
	# no_tls=True
)

# Unlock you wallet
lnd.unlock_wallet(wallet_password=b"your_wallet_password")

# Get general data about your node
lnd.get_info()

print('Listening for invoices...')
for invoice in lnd.subscribe_invoices():
    print(invoice)
```

## Advanced Usage
Go in the `examples` folder for some advanced examples including:
- WIP: Open channel using PSBT
- Keysend Payments
- Reconnect to your peers

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
```


```python
from pathlib import Path
import shutil
import sh

# TODO: these paths are messed up
for proto in list(Path("../../../lnd/lnrpc").rglob("*.proto")):
    shutil.copy(proto, Path.cwd())

protos = list(Path(".").joinpath("lndgrpc/compiled/").glob("*.proto"))

args = [
    "-m",
    "grpc_tools.protoc",
    "--proto_path=lndgrpc/compiled/googleapis:.",
    "--python_out=.",
    "--grpc_python_out=.",
]

for protofile in protos:
        args.append(str(protofile) )

# Generate the compiled protofiles
sh.python(args)
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