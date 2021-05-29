import sys
from .client import LNDClient
from .common import get_macaroon, get_cert

MAJOR = sys.version_info[0]
MINOR = sys.version_info[1]

__version__ = "0.1.0"


# only import the async client for python 3.6+
if MAJOR == 3 and MINOR >= 6:
    from lndgrpc.aio.async_client import AsyncLNDClient
