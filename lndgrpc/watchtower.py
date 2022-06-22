from .common import watchtower, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class WatchTowerRPC(BaseClient):
    @handle_rpc_errors
    def wt_get_info(self, **kwargs):
        """
        GetInfo
        """
        response = self._watchtower_stub.GetInfo(watchtower.GetInfoRequest())
        return response