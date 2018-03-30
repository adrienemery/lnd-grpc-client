import sys

# python 2.7 - 3.4 only get the sync version
if sys.version_info.major < 3 or sys.version_info.major == 3 and sys.version.minor < 5:
    from .client import RPCClient
else:
    from .client import RPCClient, AsyncRPCClient


