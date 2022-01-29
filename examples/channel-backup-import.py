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

cp = ln.ChannelPoint(funding_txid_str="mystring", output_index=1)

backup = ln.ChannelBackup(chan_point=cp, chan_backup=b"")

b = ln.ChannelBackups(chan_backups=[backup])

a = ln.ChanBackupSnapshot(single_chan_backups=b)

m = ln.MultiChanBackup(multi_chan_backup=c)
a = ln.ChanBackupSnapshot(multi_chan_backup=c)

fp = "/home/skorn/.polar/networks/1/volumes/lnd/bob/data/chain/bitcoin/regtest/channel.backup"

with open(fp, "rb") as f:
	c = f.read()

lnd.restore_channel_backups(multi_chan_backup=c)