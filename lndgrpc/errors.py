import grpc
from functools import wraps


class WalletEncryptedError(Exception):

    def __init__(self, message=None):
        message = message or 'Wallet is encrypted. Please unlock or set ' \
                             'password if this is the first time starting lnd. '
        super().__init__(message)


def handle_rpc_errors(fnc):
    """Decorator to add more context to RPC errors"""

    @wraps(fnc)
    def wrapper(*args, **kwargs):
        try:
            return fnc(*args, **kwargs)
        except grpc.RpcError as exc:
            # lnd might be active, but not possible to contact
            # using RPC if the wallet is encrypted. If we get
            # an rpc error code Unimplemented, it means that lnd is
            # running, but the RPC server is not active yet (only
            # WalletUnlocker server active) and most likely this
            # is because of an encrypted wallet.
            if exc.code() == grpc.StatusCode.UNIMPLEMENTED:
                raise WalletEncryptedError from None
            else:
                raise exc
    return wrapper
