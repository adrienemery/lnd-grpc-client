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
tls = str(credential_path.joinpath("tls.cert").absolute())

lnd_ip_port = f"{node_ip}:10009"

lnd = LNDClient(
	lnd_ip_port,
	macaroon_filepath=mac,
	cert_filepath=tls
	# no_tls=True
)

# lnd = AsyncLNDClient(
# 	f"{node_ip}:10009",
# 	macaroon_filepath=mac,
# 	cert_filepath=tls
# )



psbt_shim = ln.PsbtShim(
    pending_chan_id=secrets.token_bytes(32),
    no_publish=True
)

shim = ln.FundingShim(
    psbt_shim=psbt_shim
)

r = lnd.open_channel(
    node_pubkey="035ac40a32530f45078b68a381575064920fd3c7b5c658da220bec030d0202a535",
    local_funding_amount=75000,
    sat_per_byte=0,
    funding_shim=shim,
)


for i in lnd.open_channel(
    sat_per_byte=0,
    node_pubkey="035ac40a32530f45078b68a381575064920fd3c7b5c658da220bec030d0202a535",
    local_funding_amount=75000,
    funding_shim=shim,
):
 type(i)

