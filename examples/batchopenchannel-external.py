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


batch_list = [
    # {
    #     "pk":"0390cc12f782259427bdc45a283705f4c20ccbdff064ed43f6b74fefcafe9eb1f7",
    #     "url": "4ktdvcvhuytnj3hermy3fiqtj5b7lzspjzdhsgg6xafc6tjrvik6q4ad.onion:9735",
    #     "amount": 1_000_000
    # },
    {
        "pk": "03c608c491495bdf9305344728ce42170f12c5c84be6278bfa25dc04479ca988b6",
        "url": "m7haegyzvhx5rd7wqf5lfs2gc3aqxdn2trowwbqp6hybyf4l4s67jdad.onion:9735",
        "amount": 1_000_000
    },
    {
        "pk": "035b1ff29e8db1ba8f2a4f4f95db239b54069cb949b8cde329418e2a83da4f1b30",
        "url": "a3ufedotixjimo7g62c7m7zijbtmcalx33xl53ifzcyuogu3v3ceppyd.onion:9735",
        "amount": 1_000_000
    },
    {
        "pk": "03aa49c1e98ff4f216d886c09da9961c516aca22812c108af1b187896ded89807e",
        "url": "m3keajflswtfq3bw4kzvxtbru7r4z4cp5stlreppdllhp5a7vuvjzqyd.onion:9735",
        "amount": 1_000_000
    }
]

num_channels = len(batch_list)

# Ensure you are peering with the nodes
for node in batch_list:
    lnd.connect_peer(node["pk"], node["url"])

pending_cids = []

# Do one thing for all but last node
for node in batch_list[:-1]:
    pending_cid = secrets.token_bytes(32)
    pending_cids.append(pending_cid)
    psbt_shim = ln.PsbtShim(
        pending_chan_id=pending_cid,
        no_publish=True
    )
    shim = ln.FundingShim(
        psbt_shim=psbt_shim
    )
    r = lnd.open_channel(
        node_pubkey=node["pk"],
        local_funding_amount=node["amount"],
        sat_per_byte=0,
        funding_shim=shim,
    )
    print(f"Send {r.psbt_fund.funding_amount} sats to address: {r.psbt_fund.funding_address}")

pending_cid = secrets.token_bytes(32)
pending_cids.append(pending_cid)
psbt_shim = ln.PsbtShim(
    pending_chan_id=pending_cid,
    no_publish=False
)
shim = ln.FundingShim(
    psbt_shim=psbt_shim
)
r = lnd.open_channel(
    node_pubkey=batch_list[-1]["pk"],
    local_funding_amount=batch_list[-1]["amount"],
    sat_per_byte=0,
    funding_shim=shim,
)
print(f"Send {r.psbt_fund.funding_amount} sats to address: {r.psbt_fund.funding_address}")

# *** Create the funding transaction in Sparrow Wallet, and save as a PSBT ***

# Open the PSBT
with open("/home/skorn/Downloads/openchannel.psbt","rb") as f:
    unsigned = f.read()

for cid in pending_cids[:-1]:
    verify = ln.FundingPsbtVerify(funded_psbt=unsigned, pending_chan_id=cid)
    lnd.funding_state_step(psbt_verify=verify)

verify = ln.FundingPsbtVerify(funded_psbt=unsigned, pending_chan_id=pending_cids[-1], skip_finalize=False)
lnd.funding_state_step(psbt_verify=verify)

# *** signed the funding transaction and save

with open("/home/skorn/Downloads/openchannel.txn","r") as f:
    signed = f.read()

rawtx = bytes.fromhex(signed)


for cid in pending_cids[:-1]:
    final = ln.FundingPsbtFinalize(final_raw_tx=rawtx, pending_chan_id=cid)
    lnd.funding_state_step(psbt_finalize=final)


final = ln.FundingPsbtFinalize(final_raw_tx=rawtx, pending_chan_id=pending_cids[-1])
lnd.funding_state_step(psbt_finalize=final)

# OPTIONALLY CANCEL THE CHANNEL(s)
# SKIP THIS
for cid in pending_cids:
    cancel_shim = ln.FundingShimCancel(pending_chan_id=cid)
    lnd.funding_state_step(shim_cancel=cancel_shim)