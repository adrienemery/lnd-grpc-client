from .common import autopilot, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class AutoPilotRPC(BaseClient):
    @handle_rpc_errors
    def modify_status(self):
        """
        ModifyStatus
        """
        response = self._autopilot_stub.GetState(stateservice.GetStateRequest())
        return response

    @handle_rpc_errors
    def query_scores(self):
        """
        QueryScores
        """
        response = self._autopilot_stub.GetState(stateservice.GetStateRequest())
        return response

    @handle_rpc_errors
    def set_scores(self):
        """
        SetScores
        """
        response = self._autopilot_stub.GetState(stateservice.GetStateRequest())
        return response


    @handle_rpc_errors
    def status(self):
        """
        Status
        """
        response = self._autopilot_stub.Status(autopilot.StatusRequest())
        return response