import binascii
import platform
import os
import grpc
from . import rpc_pb2, rpc_pb2_grpc

ln = rpc_pb2
lnrpc = rpc_pb2_grpc


system = platform.system().lower()
if system == 'linux':
    TLS_FILEPATH = os.path.expanduser('~/.lnd/tls.cert')
    ADMIN_MACAROON_FILEPATH = os.path.expanduser('~/.lnd/admin.macaroon')
    READ_ONLY_MACAROON_FILEPATH = os.path.expanduser('~/.lnd/readonly.macaroon')
elif system == 'darwin':
    TLS_FILEPATH = os.path.expanduser('~/Library/Application Support/Lnd/tls.cert')
    ADMIN_MACAROON_FILEPATH = os.path.expanduser('~/Library/Application Support/Lnd/admin.macaroon')
    READ_ONLY_MACAROON_FILEPATH = os.path.expanduser('~/Library/Application Support/Lnd/readonly.macaroon')
else:
    raise SystemError('Unrecognized system')


# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handhsake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'


def get_cert(filepath=None):
    """Read in tls.cert from file

    Note: tls files need to be read in byte mode as of grpc 1.8.2
          https://github.com/grpc/grpc/issues/13866
    """
    filepath = filepath or TLS_FILEPATH
    with open(filepath, 'rb') as f:
        cert = f.read()
    return cert


def get_macaroon(filepath=None):
    """Read and decode macaroon from file

    The macaroon is decoded into a hex string and returned.
    """
    filepath = filepath or READ_ONLY_MACAROON_FILEPATH
    with open(filepath, 'rb') as f:
        macaroon_bytes = f.read()
    return binascii.hexlify(macaroon_bytes).decode()


def generate_credentials(cert, macaroon):
    """Create composite channel credentials using cert and macaroon metatdata"""
    # create cert credentials from the tls.cert file
    cert_creds = grpc.ssl_channel_credentials(cert)

    # build meta data credentials
    metadata_plugin = MacaroonMetadataPlugin(macaroon)
    auth_creds = grpc.metadata_call_credentials(metadata_plugin)

    # combine the cert credentials and the macaroon auth credentials
    # such that every call is properly encrypted and authenticated
    return grpc.composite_channel_credentials(cert_creds, auth_creds)


class MacaroonMetadataPlugin(grpc.AuthMetadataPlugin):
    """Metadata plugin to include macaroon in metadata of each RPC request"""

    def __init__(self, macaroon):
        self.macaroon = macaroon

    def __call__(self, context, callback):
        callback([('macaroon', self.macaroon)], None)


class BaseClient(object):
    grpc_module = grpc

    def __init__(self, ip_address, cert=None, cert_filepath=None, macaroon=None, macaroon_filepath=None):
        if cert is None:
            cert = get_cert(cert_filepath)

        if macaroon is None:
            macaroon = get_macaroon(macaroon_filepath)

        if cert is None:
            cert = get_cert(cert_filepath)

        if macaroon is None:
            macaroon = get_macaroon(macaroon_filepath)

        self._credentials = generate_credentials(cert, macaroon)
        self.ip_address = ip_address

    @property
    def _ln_stub(self):
        """Create a ln_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(self.ip_address, self._credentials)
        return lnrpc.LightningStub(channel)

    @property
    def _wallet_stub(self):
        """Create a wallet_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(self.ip_address, self._credentials)
        return lnrpc.WalletUnlockerStub(channel)
