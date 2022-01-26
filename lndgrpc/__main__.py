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


credential_path = Path(os.getenv("CRED_PATH"))

mac = str(credential_path.joinpath("admin.macaroon").absolute())
tls = str(credential_path.joinpath("tls.cert").absolute())
node_ip = os.getenv("LND_NODE_IP")

lnd = LNDClient(
	f"{node_ip}:10009",
	macaroon_filepath=mac,
	cert_filepath=tls
)

pprint(protobuf_to_dict(lnd.get_info()))

print("lndgrpc package is installed... Wow it works!")
