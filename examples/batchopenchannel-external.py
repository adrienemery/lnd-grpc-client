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


pk_connect1 = "0201aeb7f1b28c0b8244d4b214ca137f72870a0e52f9f53debe80eb403ffcd6a99@69.197.185.106:9745".split("@")
pk_connect2 = "0241bc65c496503b1dd27bc80379cb959fb82ad26673d237b3c8f59289fb99742f@217.173.236.77:29735".split("@")
pk_connect3 = "03ee83ec25fc43cf1d683be47fd5e2ac39713a489b03fed4350d9623be1ff0d817@203.86.204.88:9745".split("@")


lnd.connect_peer(pk_connect1[0], pk_connect1[1])
lnd.connect_peer(pk_connect2[0], pk_connect2[1])
lnd.connect_peer(pk_connect3[0], pk_connect3[1])

pk1 = pk_connect1[0]
pk2 = pk_connect2[0]
pk3 = pk_connect3[0]


pending_cid1 = secrets.token_bytes(32)

psbt_shim1 = ln.PsbtShim(
    pending_chan_id=pending_cid1,
    no_publish=True
)

shim1 = ln.FundingShim(
    psbt_shim=psbt_shim1
)

pending_cid2 = secrets.token_bytes(32)


psbt_shim2 = ln.PsbtShim(
    pending_chan_id=pending_cid2,
    no_publish=True
)

shim2 = ln.FundingShim(
    psbt_shim=psbt_shim2
)

pending_cid3 = secrets.token_bytes(32)


psbt_shim3 = ln.PsbtShim(
    pending_chan_id=pending_cid3,
    no_publish=False
)

shim3 = ln.FundingShim(
    psbt_shim=psbt_shim3
)

r = lnd.open_channel(
    node_pubkey=pk1,
    local_funding_amount=900_000,
    sat_per_byte=0,
    funding_shim=shim1,
)
#

r = lnd.open_channel(
    node_pubkey=pk2,
    local_funding_amount=900_000,
    sat_per_byte=0,
    funding_shim=shim2,
)
#
r = lnd.open_channel(
    node_pubkey=pk3,
    local_funding_amount=900_000,
    sat_per_byte=0,
    funding_shim=shim3,
)
#

with open("/home/skorn/Downloads/openchannel.psbt",'rb') as f:
    unsigned = f.read()

verify1 = ln.FundingPsbtVerify(funded_psbt=unsigned, pending_chan_id=pending_cid1)
lnd.funding_state_step(psbt_verify=verify1)

verify2 = ln.FundingPsbtVerify(funded_psbt=unsigned, pending_chan_id=pending_cid2)
lnd.funding_state_step(psbt_verify=verify2)

verify3 = ln.FundingPsbtVerify(funded_psbt=unsigned, pending_chan_id=pending_cid3, skip_finalize=False)
lnd.funding_state_step(psbt_verify=verify3)

# with open("/home/skorn/Downloads/openchannel-signed.psbt",'rb') as f:
#     signed = f.read()

rawtx = bytes.fromhex("0200000000010140cb40e9d987e7237aa5540c9750649ab9906d3d65d2a11a15290b23fbb052ce0000000000fdffffff04a0bb0d000000000022002020783080062384c271fe4fb90da0b95aa8671325f4bd27a165171b1a93570df3f192040000000000160014c68760e0e74c6ee3f54832a8cb856c9b6ccb4fcfa0bb0d00000000002200202c99a9cc3a071bcf035c628c54801358d8fda2599130af547b69e5ddce330ff7a0bb0d0000000000220020199c8fb904c65fb32eddb2f2dd8c60cbce8ffb549885052e0386da7559bddc5e02473044022015833403b5e8288ecfdccc81949cadef04c9064d022824587401f6d056f0d8de022062aa2c2e83064315fd73b00feba5dcf450dbe6a27f121a7e276eb2c81392726c012103bfc69867af277998ad10466e16cdbb34391d955527e36c9276df0d36d237619f08202000")

# signed_psbt (bytes) or final_raw_tx (bytes) wire format


final1 = ln.FundingPsbtFinalize(final_raw_tx=rawtx, pending_chan_id=pending_cid1)
lnd.funding_state_step(psbt_finalize=final1)

final2 = ln.FundingPsbtFinalize(final_raw_tx=rawtx, pending_chan_id=pending_cid2)
lnd.funding_state_step(psbt_finalize=final2)

final3 = ln.FundingPsbtFinalize(final_raw_tx=rawtx, pending_chan_id=pending_cid3)
lnd.funding_state_step(psbt_finalize=final3)
# OPTIONALLY CANCEL THE CHANNEL(s)
# SKIP THIS
cancel_shim = ln.FundingShimCancel(pending_chan_id=pending_cid)

lnd.funding_state_step(shim_cancel=cancel_shim)