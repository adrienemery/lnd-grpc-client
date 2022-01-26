from pathlib import Path
import json
from pprint import pprint
import os
import base64
from time import sleep
from datetime import datetime, timedelta

from hashlib import sha256
import secrets

# Pip installed Modules
from lndgrpc import LNDClient
from lndgrpc.client import ln
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
# Create hop/route hints if the node only has private channels
hint1 = ln.HopHint(
	node_id="031015a7839468a3c266d662d5bb21ea4cea24226936e2864a7ca4f2c3939836e0",
	chan_id=723616090046660608,
	fee_base_msat=1000,
	fee_proportional_millionths=1,
	cltv_expiry_delta=40
)

hint2 = ln.HopHint(
	node_id="031015a7839468a3c266d662d5bb21ea4cea24226936e2864a7ca4f2c3939836e0",
	chan_id=715661123542515712,
	fee_base_msat=1000,
	fee_proportional_millionths=1,
	cltv_expiry_delta=40
)

hint3 = ln.HopHint(
	node_id="031015a7839468a3c266d662d5bb21ea4cea24226936e2864a7ca4f2c3939836e0",
	chan_id=723785414869581824,
	fee_base_msat=1000,
	fee_proportional_millionths=1,
	cltv_expiry_delta=40
)

hint4 = ln.HopHint(
	node_id="031015a7839468a3c266d662d5bb21ea4cea24226936e2864a7ca4f2c3939836e0",
	chan_id=729142235565260800,
	fee_base_msat=1000,
	fee_proportional_millionths=1,
	cltv_expiry_delta=40
)
routehint = ln.RouteHint(hop_hints=[hint1,hint2,hint3,hint4])


# Setup
keySendPreimageType = 5482373484
messageType = 34349334
preimageByteLength = 32
preimage = secrets.token_bytes(preimageByteLength)
m = sha256()
m.update(preimage)
preimage_hash = m.digest()

dest_custom_records = {
        keySendPreimageType: preimage,
		messageType: "wow a keysend!".encode()
}

random_bytes = secrets.token_bytes(32)


# send using sendpayment
lnd.send_payment_v2(
	# payment_addr=random_string,
	dest=bytes.fromhex("0353c8638e6663b338f79d06cc4648f993c36f5d1c8a32709518064270cb0df55e"),
	amt=10,
	payment_hash=preimage_hash,
	dest_custom_records=dest_custom_records,
	timeout_seconds=16,
	dest_features=[9],
	fee_limit_msat=100000,
	max_parts=1,
	final_cltv_delta=144,
	cltv_limit=148,
	amp=False,
	route_hints=[routehint]
)


# send using a route

# test node
route = lnd.query_routes(
	"02796793ccc5da92528a5c7455351ebdc203c155e179796aa59fd28f73e1af7c10",
	12,
	route_hints=[routehint]
).routes[0]

route.hops[-1].custom_records.update(dest_custom_records)

lnd.send_to_route(
    pay_hash = preimage_hash,
    route=route
)


# private node
route = lnd.query_routes(
	"0353c8638e6663b338f79d06cc4648f993c36f5d1c8a32709518064270cb0df55e",
	12,
	route_hints=[routehint]
).routes[0]

route.hops[-1].custom_records.update(dest_custom_records)

lnd.send_to_route(
    pay_hash = preimage_hash,
    route=route
)




# https://github.com/alexbosworth/lightning/blob/master/lnd_requests/rpc_route_from_route.js#L72
# https://github.com/alexbosworth/ln-service/blob/master/test/invoicesrpc-integration/test_push_payment.js#L40
# https://github.com/stakwork/sphinx-relay/blob/fa2b22d23ef75a041783e7ef512a513d635121f6/src/grpc/lightning.ts#L290-L384