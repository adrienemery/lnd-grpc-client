from pathlib import Path
import json
from pprint import pprint
import os
import base64
from time import sleep
from datetime import datetime, timedelta

# Pip installed Modules
from lndgrpc import LNDClient
from lndgrpc.common import ln
from protobuf_to_dict import protobuf_to_dict

from pymacaroons import Macaroon, Verifier

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

uris = [ uri for uri in lnd.list_permissions().method_permissions ]
perms = []

for uri in uris:
    perm = lnd.list_permissions().method_permissions[uri].permissions[0]
    if perm not in perms:
        perms.append(perm)

# you can also use specific URI permissions
p = [ ln.MacaroonPermission(entity="uri", action="/lnrpc.Lightning/ListMacaroonIDs") ]

# Just grab a handful of permissions for the test
p = perms[0:10]

baked = lnd.bake_macaroon(
    permissions_list=p,
    root_key_id=5
)

credential_path = Path(credential_path)
baked_mac = credential_path.joinpath("test1234.macaroon")
with open(baked_mac,"wb") as f:
    f.write(bytes.fromhex(baked.macaroon))


# 1st party caveats not working yet
baked_64 = base64.b64encode(bytearray.fromhex(baked.macaroon)).decode()

n = Macaroon.deserialize(baked_64)
n.add_first_party_caveat('ipaddr 192.168.1.1')
n.add_first_party_caveat('time-before {ISO 8601 Date}')
serialized = n.serialize()