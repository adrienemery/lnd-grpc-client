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


pending_cid = secrets.token_bytes(32)

psbt_shim = ln.PsbtShim(
    pending_chan_id=pending_cid,
    no_publish=False
)




shim = ln.FundingShim(
    psbt_shim=psbt_shim
)

r = lnd.open_channel(
    node_pubkey="02312627fdf07fbdd7e5ddb136611bdde9b00d26821d14d94891395452f67af248",
    local_funding_amount=1000000,
    sat_per_byte=0,
    funding_shim=shim,
)


cp_shim = ln.ChanPointShim(
    amt=1000000,
    chan_point=ln.ChannelPoint(
        funding_txid_str="83868837f1a8f3d9657513d9ca7c2fc93e6a8bac58b3fe132dddb051140eca99",
        output_index=1
    )
)

shim = ln.FundingShim(
    chan_point_shim=cp_shim
)

lnd.funding_state_step(shim_register=shim)


cancel_shim = ln.FundingShimCancel(pending_chan_id=pending_cid)

lnd.funding_state_step(shim_cancel=cancel_shim)

with open("/home/skorn/Downloads/openchannel.psbt",'rb') as f:
    unsigned = f.read()

# verify = ln.FundingPsbtVerify(funded_psbt=unsigned, pending_chan_id=pending_cid, skip_finalize=False)
verify = ln.FundingPsbtVerify(funded_psbt=unsigned, pending_chan_id=pending_cid)
lnd.funding_state_step(psbt_verify=verify)

with open("/home/skorn/Downloads/openchannel-signed.psbt",'rb') as f:
    signed = f.read()

rawtx = bytes.fromhex("0200000000010112e3f6f52d34e7bc357244a68a313f9b4c0b2d371a343734f0694d394010fec70100000000fdffffff0240420f00000000002200209b48384000f4c7c62dc4738eb713d5e4f3a659eee77677cbb101718f865d1297e7831e00000000001600142387319e0db1ed1426cacccc513a93aa8d512bcb02473044022059d84cd054013c7a85ffbc01fc880bd2463bf1f2b85ad4145cd011243205e39902207c22408de1aa3fae2d9a44c8193baa1803b1b1a791eb47ded79afa7dfc68cca6012102c835cdb852c781e5df4a3a0fcf2c0989ab640998de32d8e233995ef10986926fd31f2000")
# signed_psbt (bytes) or final_raw_tx (bytes) wire format
final = ln.FundingPsbtFinalize(signed_psbt=signed, pending_chan_id=pending_cid)
final = ln.FundingPsbtFinalize(final_raw_tx=rawtx, pending_chan_id=pending_cid)


lnd.funding_state_step(psbt_finalize=final)


for i in lnd.open_channel(
    sat_per_byte=0,
    node_pubkey="035ac40a32530f45078b68a381575064920fd3c7b5c658da220bec030d0202a535",
    local_funding_amount=75000,
    funding_shim=shim,
):
 type(i)

