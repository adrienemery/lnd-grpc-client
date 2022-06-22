from .common import ver, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class VersionerRPC(BaseClient):
    @handle_rpc_errors
    def get_version(self, **kwargs):
        """
        GetVersion
        """
        request = ver.VersionRequest()
        response = self._version_stub.GetVersion(request)
        return response
