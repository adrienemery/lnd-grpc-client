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


for chan in lnd.list_channels().channels:
	if chan.active:
		continue
	pk = chan.remote_pubkey
	node_info = lnd.get_node_info(pk, include_channels=False)
	alias = node_info.node.alias
	all_addresses = node_info.node.addresses
	for address in all_addresses:
		lnd.connect_peer(pk, address.addr)
	print(f"connected to: {alias}")