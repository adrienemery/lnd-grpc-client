from pathlib import Path
import json
from pprint import pprint
import os
import base64
from time import sleep
from datetime import datetime, timedelta

# Pip installed Modules
from lndgrpc import LNDClient
from protobuf_to_dict import protobuf_to_dict

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

import code
code.interact(local=dict(globals(), **locals())) 

lnd.get_info().alias



