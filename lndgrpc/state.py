from .common import stateservice, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class StateRPC(BaseClient):
    @handle_rpc_errors
    def get_state(self):
        """
        GetState
        """
        response = self._state_stub.GetState(stateservice.GetStateRequest())
        return response

    @handle_rpc_errors
    def subscribe_state(self):
        """
        SubscribeState
        """
        response = self._state_stub.GetState(stateservice.SubscribeStateRequest())
        return response