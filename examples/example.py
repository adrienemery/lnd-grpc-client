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

credential_path = Path("/home/skorn/.lnd")

mac = str(credential_path.joinpath("data/chain/bitcoin/mainnet/admin.macaroon").absolute())
tls = str(credential_path.joinpath("tls.cert").absolute())


lnd = LNDClient(
	"127.0.0.1:10009",
	macaroon_filepath=mac,
	cert_filepath=tls
)