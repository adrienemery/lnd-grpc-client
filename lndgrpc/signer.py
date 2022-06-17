from .common import signer, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class SignerRPC(BaseClient):
    # SIGNERRPC
    @handle_rpc_errors
    def signer_sign_message(self, msg, key_family, key_index):
        key_loc = signer.KeyLocator(key_family=key_family,key_index=key_index)
        request = signer.SignMessageReq(
            msg=msg,
            key_loc=key_loc
        )
        response = self._signer_stub.SignMessage(request)
        return response

    @handle_rpc_errors
    def signer_verify_message(self, msg, signature, pubkey):
        request = signer.VerifyMessageReq(
            msg=msg,
            signature=signature,
            pubkey=pubkey
        )
        response = self._signer_stub.VerifyMessage(request)
        return response