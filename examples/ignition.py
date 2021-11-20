from pathlib import Path
import json
from pprint import pprint
import os
import base64
from time import sleep
from datetime import datetime, timedelta

from hashlib import sha256
import secrets

from yachalk import chalk



# Pip installed Modules
from lndgrpc.client import LNDClient
from lndgrpc.client import ln
from protobuf_to_dict import protobuf_to_dict

TLS_FILEPATH = os.path.expanduser('/Users/ziggie/working_freetime/lnd-grpc-client/lnd_credentials/tls.cert')
ADMIN_MACAROON_BASE_FILEPATH = '/Users/ziggie/working_freetime/lnd-grpc-client/lnd_credentials/admin.macaroon'
READ_ONLY_MACAROON_BASE_FILEPATH = '/Users/ziggie/working_freetime/lnd-grpc-client/lnd_credentials/readonly.macaroon'
NODE_IP = "192.168.178.22"


lnd = LNDClient(
	f"{NODE_IP}:10009",
    macaroon_filepath=ADMIN_MACAROON_BASE_FILEPATH,
    cert_filepath=TLS_FILEPATH
)

mypk = lnd.get_info().identity_pubkey
myalias = lnd.get_info().alias


file = '/Users/ziggie/working_freetime/lnd-grpc-client/pubkey.txt'
with open(file) as file:
    pubkeys = file.read().splitlines()

pubkeysReorderedForIgnition = []
#First Reorder Pubkeys so that my node is the first
for idx, pubkeyInfo in enumerate(pubkeys):
        # pubkeys formatis <pubkey>,<telegram username> to be able to mimic the manual pubkey overview with usernames
        pubkey = pubkeyInfo.split(',')
        #print(pubkey)
        if pubkey[0] == mypk:
            reorder_id = idx + 1 % len(pubkeys)
            pubkeysReorderedForIgnition = pubkeys[reorder_id:len(pubkeys)] + pubkeys[:reorder_id]
            print("\n".join(map(str, pubkeysReorderedForIgnition)))
            exit

#Check whether each Channel has a channel with the node

rofIgnitionPossible = True
outgoing_chan_id = 0
hop_pubkeys = []

print(chalk.bold("Channel Overview about the ROF"))
print("="*50)
print("="*50)
for idx, pubkeyInfo in enumerate(pubkeysReorderedForIgnition):



    try:
        pubkey = pubkeyInfo.split(',')
        channelTo = pubkeysReorderedForIgnition[(idx+1) % (len(pubkeysReorderedForIgnition))].split(',')[0]
        channelToAlias = pubkeysReorderedForIgnition[(idx+1) % (len(pubkeysReorderedForIgnition))].split(',')[1]
        nodeResponse = lnd.get_node_info(pubkey[0])

        hasChannel = False
        channelID = 0
        channelInfo = {}

        hop_pubkeys.append(pubkey[0])

        for channel in nodeResponse.channels:
            if (channel.node1_pub == channelTo or channel.node2_pub == channelTo):
                hasChannel = True
                channelID = channel.channel_id
                channelInfo = channel
                if pubkey == pubkeysReorderedForIgnition[-1].split(',')[0]:
                    outgoing_chan_id = channelID
                exit

        if hasChannel:
            #Check if Channel is disabled
            chanResponse = lnd.get_chan_info(channelID)
            node1Disabled = chanResponse.node1_policy.disabled
            node2Disabled = chanResponse.node2_policy.disabled
            if not node1Disabled and not node2Disabled:
                print(chalk.green("Channel exist ✅ :\n%s opened to  %s ChannelID  %s  " % (pubkey[1],channelToAlias, channelID)))
                print("-"*50)
            else:
                print(chalk.yellow("Channel exist ❗️ but Disabled, Try Reconnect to Peer :\n%s opened to  %s ChannelID  %s  " % (pubkey[1],channelToAlias, channelID)))
                print("-"*50)
        else:
            rofIgnitionPossible = False
            print(chalk.red("Channel STILL NOT OPEN  🆘 :\n%s has to open with %s" % (pubkey[1],channelToAlias)))
            print("-"*50)





    except Exception as error:
        print(error)

if True:

    amt_msat = 1000
    route = lnd.build_route(amt_msat,outgoing_chan_id,hop_pubkeys)
    print(route)
