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

import csv

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
node_port = os.getenv("LND_NODE_PORT")
tls = str(credential_path.joinpath("tls.cert").absolute())

lnd_ip_port = f"{node_ip}:{node_port}"

lnd = LNDClient(
	lnd_ip_port,
	macaroon_filepath=mac,
	cert_filepath=tls
	# no_tls=True
)

batch_list = [
    {
        "pk": "02d10ee0e69020791ceb98605f7f4b4ee4400b4ab1745480aabc2c1205bb7d0a7d",
        "url": "172.18.0.5:9735",
        "amount": 1_000_000
    } for i in range(0,100)
]

num_channels = len(batch_list)

# Ensure you are peering with the nodes
for node in batch_list:
    lnd.connect_peer(node["pk"], node["url"])

pending_cids = []
output_csv = []

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
    output_csv.append((r.psbt_fund.funding_address,r.psbt_fund.funding_amount,"fund"))

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
output_csv.append((r.psbt_fund.funding_address,r.psbt_fund.funding_amount,"fund"))


with open('multi-open.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, dialect='excel')
    # for addr, amt, msg in output_csv:
    for a in output_csv:
        spamwriter.writerow(a)


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



psbt_shim = ln.PsbtShim(
    pending_chan_id=pending_cid,
    no_publish=False
)
shim = ln.FundingShim(
    psbt_shim=psbt_shim
)
r = lnd.open_channel(
    node_pubkey=batch_list[0]["pk"],
    local_funding_amount=20000,
    sat_per_byte=0,
    funding_shim=shim,
)