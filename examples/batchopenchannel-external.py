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
    #     "pk": "028d1db1af4ba4982e4dd71c6e4167065602021f34006c9bef683dc57d053df4e9",
    #     "url": "7p3j2yumw5cvxyg3eyjcqkjhsqyfaukydep7vfd76whrc5hjlizsmfid.onion:9735",
    #     "amount": 1_000_000
    # },
    # {
    #     "pk": "027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71",
    #     "url": "yi6ccghmivsydduxb2wnogyx2chz347bgu3kvqefea7rnhfi5iifqcyd.onion:9735",
    #     "amount": 1_000_000
    # },
    {
        "pk": "02ae53b0661195617ba1063e053ee238a24e80b90e371ebf2038de00aeb196bfd7",
        "url": "zp4rwdr2efjl534bp7qwblrjfaz5thwban5xbf6vf6nncbv56ksxowyd.onion:9735",
        "amount": 1_000_000
    },
    {
        "pk": "031f2669adab71548fad4432277a0d90233e3bc07ac29cfb0b3e01bd3fb26cb9fa",
        "url": "i4hkz4tgek4urajnkghf5pdyncpbso72lxdkapanrxt54mtr54t5xvqd.onion:9735",
        "amount": 1_000_000
    },
    {
        "pk": "022926ac1f1f472e669b1802488f5acfa75adf2020cec28e199e4c61f6485e8b41",
        "url": "tui6tgdlxznkk3uymvat3omb7e7636vdokrxnfkorfjbstvq5mdyjnyd.onion:9735",
        "amount": 1_000_000
    },
    {
        "pk": "03c5528c628681aa17ab9e117aa3ee6f06c750dfb17df758ecabcd68f1567ad8c1",
        "url": "zacadqiqgi43tdv4ztjet2fh22f72ol2tokotp5cqdbszgx6tpyqdxad.onion:9735",
        "amount": 2_169_420
    },
    {
        "pk": "025f1456582e70c4c06b61d5c8ed3ce229e6d0db538be337a2dc6d163b0ebc05a5",
        "url": "52.86.210.65:9735",
        "amount": 1_000_000
    },
    # {
    #     "pk": "034b025cd658515f37bb125b6ef040f428b0ce678253c805358e9db60c40d9f96a",
    #     "url": "ohcwnk5p5neseibf7dukxtbji6ytzh2jo7yki6wds76jiwv3sigabwyd.onion:9735",
    #     "amount": 1_000_000
    # },  
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