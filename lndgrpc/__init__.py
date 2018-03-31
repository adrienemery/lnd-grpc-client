import sys
from .client import LNDClient

MAJOR = sys.version_info[0]
MINOR = sys.version_info[1]

# only import the async client for python 3.5+
if MAJOR == 3 and MINOR >= 5:
    from lndgrpc.async.async_client import AsyncLNDClient
