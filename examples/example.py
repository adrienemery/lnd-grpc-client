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
	credential_path = Path("/home/skorn/.lnd/")
	mac = str(credential_path.joinpath("data/chain/bitcoin/mainnet/admin.macaroon").absolute())
else:
	credential_path = Path(credential_path)
	mac = str(credential_path.joinpath("admin.macaroon").absolute())
	

node_ip = "192.168.1.58"
tls = str(credential_path.joinpath("tls.cert").absolute())


lnd = LNDClient(
	f"{node_ip}:10009",
	macaroon_filepath=mac,
	cert_filepath=tls
)

lnd.get_info()