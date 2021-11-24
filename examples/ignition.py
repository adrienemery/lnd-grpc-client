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

mypk = lnd.get_info().identity_pubkey
myalias = lnd.get_info().alias
pubkeysReorderedForIgnition = []

########ITEMS TO CHANGE#################
#CHANGE THE AMOUNT
AMOUNT_SATS = 1
#IF FALSE, Payment will only queried
FINAL_PAYMENT = True

#This script parses a pubkey txt file with the following structures pubkey,@telegramname
#02b2d5b1e3167287ea4d1835e5272d99f7beb8c283f7a27d15198270630d3eb23a,@hippiesabotage
#034997db2fa4563a86b0a06103944ad8eb5c2ff013e58afaa90f3de8a7bfd2b6d6,@ECB
#02826f50035eca93c7ebfbad4f9621a8eb201f4e28f994db5b6b5af32a65efb6b9,@Anathos
#0258adfbecc79c65f5d32ff0d7e9da6dc5e765140a8e8de7ed5ca0c6a4f6d37fb3,@altbierjupp
#02bc320249b608a53a76cf3cbd448fdd3ab8f3766f96e8649c2edc26cf03bf8277,@spast

file = 'PATHTO/pubkey.txt'




with open(file) as file:
    pubkeys = file.read().splitlines()

#First Reorder Pubkeys so that my node is the first
for idx, pubkeyInfo in enumerate(pubkeys):
        # pubkeys formatis <pubkey>,<telegram username> to be able to mimic the manual pubkey overview with usernames
        pubkey = pubkeyInfo.split(',')
        #print(pubkey)
        if pubkey[0] == mypk:
            reorder_id = idx + 1 % len(pubkeys)
            pubkeysReorderedForIgnition = pubkeys[reorder_id:len(pubkeys)] + pubkeys[:reorder_id]
            #print("\n".join(map(str, pubkeysReorderedForIgnition)))
            break

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
                break

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

if rofIgnitionPossible:

	print(chalk.green("Ignition in 3 2 1: 🚀"))

	route = lnd.build_route(AMOUNT_SATS*1000,outgoing_chan_id,hop_pubkeys).route



	inv = lnd.add_invoice(AMOUNT_SATS,"rebalance")
	pr = lnd.decode_pay_req(inv.payment_request)


	if FINAL_PAYMENT:
		route.hops[-1].mpp_record.total_amt_msat = pr.num_msat
		route.hops[-1].mpp_record.payment_addr = pr.payment_addr


	payment = lnd.send_to_route(
	    pay_hash = bytes.fromhex(pr.payment_hash),
	    route=route
	)
	#print(payment.status)
	if (int(payment.status) == 2):
		print(chalk.red("FAILED 🚑 ❌"))
		print(chalk.red(payment.failure))
		print(chalk.red(payment.route))
	elif (int(payment.status) == 1):
		print(chalk.green("SUCCESS 🍻"))
		print(chalk.green(payment.route))
