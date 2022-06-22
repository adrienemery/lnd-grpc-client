from .common import dev, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class DevRPC(BaseClient):
    @handle_rpc_errors
    def import_graph(self, nodes, edges):
        """
        ImportGraph
        """
        request = dev.ChannelGraph(
            nodes=nodes,
            edges=edges
        )
        response = self._dev_stub.ImportGraph(request)
        return response