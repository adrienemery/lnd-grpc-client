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

with open("/home/skorn/Downloads/openchannel.psbt",'rb') as f:
    unsigned = f.read()

# verify = ln.FundingPsbtVerify(funded_psbt=unsigned, pending_chan_id=pending_cid, skip_finalize=False)
verify = ln.FundingPsbtVerify(funded_psbt=unsigned, pending_chan_id=pending_cid, skip_finalize=False)
lnd.funding_state_step(psbt_verify=verify)

with open("/home/skorn/Downloads/openchannel-signed.psbt",'rb') as f:
    signed = f.read()

rawtx = bytes.fromhex("0200000000010112e3f6f52d34e7bc357244a68a313f9b4c0b2d371a343734f0694d394010fec70100000000fdffffff0240420f0000000000220020c9c9dc9c2ed31edfc3b84ed7744a4b2c541fb1f2164cb742c7bf97a70d90f56de7831e00000000001600142387319e0db1ed1426cacccc513a93aa8d512bcb02473044022034d2ec876fb8e41fb95ddb1148ef913b884f42b3ad260c5e2fd52fce55fe7eab022046bce630cd4cd43b0cf44593d285e21c65d9a496c2d27d45f3b55ef068c50bce012102c835cdb852c781e5df4a3a0fcf2c0989ab640998de32d8e233995ef10986926fd71f2000")

# signed_psbt (bytes) or final_raw_tx (bytes) wire format
# final = ln.FundingPsbtFinalize(signed_psbt=signed, pending_chan_id=pending_cid)
final = ln.FundingPsbtFinalize(final_raw_tx=rawtx, pending_chan_id=pending_cid)


lnd.funding_state_step(psbt_finalize=final)

# OPTIONALLY CANCEL THE CHANNEL
# SKIP THIS
cancel_shim = ln.FundingShimCancel(pending_chan_id=pending_cid)

lnd.funding_state_step(shim_cancel=cancel_shim)