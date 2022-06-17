from .common import walletunlocker, ver, walletkit, signer, router, ln, BaseClient, invoices
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

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