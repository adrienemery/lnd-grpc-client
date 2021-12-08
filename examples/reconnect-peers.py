from pathlib import Path
import json
from pprint import pprint
import os
import base64
from time import sleep
from datetime import datetime, timedelta
import random
import secrets
import asyncio

from lndgrpc import LNDClient, AsyncLNDClient
from lndgrpc.common import ln

credential_path = os.getenv("LND_CRED_PATH", None)
if credential_path == None:
	credential_path = Path.home().joinpath(".lnd")
	mac = str(credential_path.joinpath("data/chain/bitcoin/mainnet/admin.macaroon").absolute())
else:
	credential_path = Path(credential_path)
	mac = str(credential_path.joinpath("admin.macaroon").absolute())
	

node_ip = os.getenv("LND_NODE_IP")
node_port = os.getenv("LND_NODE_PORT")
tls = str(credential_path.joinpath("tls.cert").absolute())

lnd_ip_port = f"{node_ip}:{node_port}"

lnd = LNDClient(
	lnd_ip_port,
	macaroon_filepath=mac,
	cert_filepath=tls
	# no_tls=True
)

pk = "0219426a5b641ed05ee639bfda80c1e0199182944977686d1dd1ea2dcb89e5dd55"

node_info = ln.lnd.get_node_info(pk, include_channels=False)
all_addresses = node_info.node.addresses
if len(all_addresses) == 1:
    addr_index = 0
else:
    addr_index = 1

ln.lnd.connect_peer(pk, all_addresses[addr_index].addr)
print(f"connected to: {node_info.node.alias}")
ln.list_channels()

for address in all_addresses:
    if "onion" in address.addr:
        tor_address = address.addr