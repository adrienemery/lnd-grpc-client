from datetime import datetime
import binascii

from .common import walletunlocker, ver, walletkit, signer, router, ln, BaseClient, invoices
from .errors import handle_rpc_errors

from lndgrpc.router import RouterRPC
from lndgrpc.walletunlocker import WalletUnlockerRPC
from lndgrpc.walletkit import WalletRPC
from lndgrpc.versioner import VersionerRPC
from lndgrpc.signer import SignerRPC
from lndgrpc.lightning import LightningRPC
from lndgrpc.invoices import InvoicesRPC
from lndgrpc.peers import PeersRPC
from lndgrpc.dev import DevRPC
from lndgrpc.neutrinokit import NeutrinoRPC
from lndgrpc.autopilot import AutoPilotRPC
from lndgrpc.chainnotifier import ChainNotifierRPC
from lndgrpc.watchtower import WatchTowerRPC
from lndgrpc.watchtowerclient import WTClientRPC
from lndgrpc.state import StateRPC

class LNDClient(
    RouterRPC,
    WalletUnlockerRPC,
    WalletRPC,
    VersionerRPC,
    SignerRPC,
    LightningRPC,
    InvoicesRPC,
    PeersRPC,
    DevRPC,
    NeutrinoRPC,
    AutoPilotRPC,
    ChainNotifierRPC,
    WatchTowerRPC,
    WTClientRPC,
    StateRPC
):
    pass


def cli():
    import os
    import code
    from pathlib import Path
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

    code.interact(local=dict(globals(), **locals()))  