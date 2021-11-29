from pathlib import Path
import json
from pprint import pprint
import os
import base64
import codecs
from time import sleep
from datetime import datetime, timedelta

from hashlib import sha256
import secrets

from yachalk import chalk





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




ALL_PEERS_AVAILABLE  = True
OPENING_WITH_ALL_AVAIABLE_PEERS = False

def check(string, sub_str):
    if (string.find(sub_str) == -1):
        return False
    else:
        return True

mypk = lnd.get_info().identity_pubkey

myalias = lnd.get_info().alias
node_uris = lnd.get_info().uris
tor_node = False

for uri in node_uris:
    if check(uri,'onion'):
        tor_node = True
        break


#Possible Options to select:
#check https://api.lightning.community/?python#lnrpc-batchopenchannel
#private
#min_htlc_msat
#remote_csv_delay
#close_address
#commitment_type

channels = [
            {
                'node_pubkey' : '030c5522b1cbbd874a1d14a0c1de921bb6f55be0047be83efbf7bc4111fa2ca7a2',
                'local_funding_amount' : 25_000,
                'push_sat' : 0,
                'private' : False,
            },
            {
                'node_pubkey' : '02a73e01a8a364be77359160350724c71efdd95e4b1a646870fedfd23bffe1d37a',
                'local_funding_amount' : 25_000,
                'push_sat' : 0,
                'private' : False,
            },
			{
                'node_pubkey' : '025ca7f267ac5b3a225451df7c018a873990bf6ab7c4b7a2f639e41a29939e65a4',
                'local_funding_amount' : 25_000,
                'push_sat' : 0,
                'private' : True,
            },
            ]

FEE_PER_VBYTE = 1 # Fee for the batchopening TX

#Get Nodeinfo and then connect to nodes

for channel in channels:
    node_info = lnd.get_node_info(channel['node_pubkey'],include_channels=False)
    node_pk = node_info.node.pub_key
    for host in node_info.node.addresses:
        if check(host.addr,'onion') and not tor_node:
            print(chalk.red('Other node is on Tor and needs connect to you first'))
            continue
        connection_string = node_pk + '@' + host.addr
        lnd.connect_peer(node_pk,host.addr,ln_at_url=connection_string)

#Check if every node is connected
final_channels = []
found = False
for channel in channels:
    found = False
    for peer in lnd.list_peers().peers:

        if channel['node_pubkey'] == peer.pub_key:
            print(chalk.green("Node available %s" % peer.pub_key))
            final_channels.append(channel)
            found = True
            break

    if not found:
        node_info = lnd.get_node_info(channel['node_pubkey'],include_channels=False)
        node_pk = node_info.node.pub_key
        print(chalk.red("Following Node is not connected %s" % node_pk))
        ALL_PEERS_AVAILABLE = False




if not ALL_PEERS_AVAILABLE:
    print(chalk.yellow("set OPENING_WITH_ALL_AVAIABLE_PEERS=True if you want to BatchOpen to available Peers"))




if ALL_PEERS_AVAILABLE or OPENING_WITH_ALL_AVAIABLE_PEERS:
    try:
        pending_channels = lnd.batch_open_channel(channels=final_channels,sat_per_vbyte=FEE_PER_VBYTE,label='')
        for channel in pending_channels:
            print(chalk.yellow('TXID: %s Output: %s' % (bytes.fromhex(channel.txid),channel.output_index)))
    except:
        print(chalk.red("Error occured See non colour output"))
