import binascii
import platform
import os

import aiogrpc
import grpc

import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc


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
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'ECDHE-RSA-AES128-GCM-SHA256:' \
                                       'ECDHE-RSA-AES128-SHA256:' \
                                       'ECDHE-RSA-AES256-SHA384:' \
                                       'ECDHE-RSA-AES256-GCM-SHA384:' \
                                       'ECDHE-ECDSA-AES128-GCM-SHA256:' \
                                       'ECDHE-ECDSA-AES128-SHA256:' \
                                       'ECDHE-ECDSA-AES256-SHA384:' \
                                       'ECDHE-ECDSA-AES256-GCM-SHA384'


def get_cert():
    """Read in tls.cert from file

    Note: you need to open the file in byte mode as of grpc 1.8.2
    https://github.com/grpc/grpc/issues/13866
    """
    with open(TLS_FILEPATH, 'rb') as f:
        cert = f.read()
    return cert


def get_macaroon(read_only=True):
    """Read and decode macaroon from file

    The macaroon is decoded into a hex string and returned.
    """
    if read_only:
        filepath = READ_ONLY_MACAROON_FILEPATH
    else:
        filepath = ADMIN_MACAROON_FILEPATH
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

    def __call__(self, context, callback: grpc.AuthMetadataPluginCallback):
        callback([('macaroon', self.macaroon)], None)


class RPCClient:

    def __init__(self, ip_address, cert=None, macaroon=None):
        if cert is None:
            cert = get_cert()
        else:
            cert = cert

        if macaroon is None:
            macaroon = get_macaroon()
        else:
            macaroon = macaroon

        credentials = generate_credentials(cert, macaroon)

        # create a secure channel and stub
        channel = grpc.secure_channel(ip_address, credentials)
        self.stub = lnrpc.LightningStub(channel)

    def get_info(self):
        response = self.stub.GetInfo(ln.GetInfoRequest())
        return response

    def wallet_balance(self):
        response = self.stub.WalletBalance(ln.WalletBalanceRequest())
        return response

    def channel_balance(self):
        response = self.stub.ChannelBalance(ln.ChannelBalanceRequest())
        return response

    def list_peers(self):
        """List all active, currently connected peers"""
        response = self.stub.ListPeers(ln.ListPeersRequest())
        return response

    def list_channels(self):
        """List all open channels"""
        response = self.stub.ListChannels(ln.ListChannelsRequest())
        return response

    def open_channel(self, node_pubkey, local_funding_amount=None, push_sat=None, private=False):
        """Open a channel to an existing peer"""
        request = ln.OpenChannelRequest(
            node_pubkey=node_pubkey,
            local_funding_amount=local_funding_amount,
            push_sat=push_sat,
            private=private
        )
        response = self.stub.OpenChannel(request)
        return response

    def list_invoices(self):
        request = ln.ListInvoiceRequest()
        response = self.stub.ListInvoices(request)
        return response

    def subscribe_invoices(self):
        for invoice in self.stub.SubscribeInvoices(ln.InvoiceSubscription()):
            yield invoice

    def add_invoice(self, value, memo=''):
        request = ln.Invoice(value=value, memo=memo)
        response = self.stub.AddInvoice(request)
        return response

    def unlock(self, password):
        """Unlock encrypted wallet at lnd startup"""
        pass  # TODO

    def new_address(self):
        """Generates a new witness address"""
        request = ln.NewWitnessAddressRequest()
        response = self.stub.NewWitnessAddress(request)
        return response

    def connect_peer(self, ln_address, permanent=False):
        """Connect to a remote lnd peer"""
        request = ln.ConnectPeerRequest(addr=ln_address, perm=permanent)
        response = self.stub.ConnectPeer(request)
        return response

    def disconnect_peer(self, pub_key):
        """Disconnect a remote lnd peer identified by public key"""
        request = ln.DisconnectPeerRequest(pub_key=pub_key)
        response = self.stub.DisconnectPeer(request)
        return response

    def close_channel(self, channel_point, force=False, target_conf=None, sat_per_byte=None):
        """Close an existing channel"""
        request = ln.CloseChannelRequest(
            channel_point=channel_point,
            force=force,
            target_conf=target_conf,
            sat_per_byte=sat_per_byte
        )
        response = self.stub.CloseChannel(request)
        return response

    def pending_channels(self):
        """Display information pertaining to pending channels"""
        request = ln.PendingChannelsRequest()
        response = self.stub.PendingChannels(request)
        return response

    def send_payment(self, payment_request):
        """Send a payment over lightning"""
        request = ln.SendRequest(payment_request=payment_request)
        response = self.stub.SendPaymentSync(request)
        return response

    def lookup_invoice(self, r_hash_str):
        """Lookup an existing invoice by its payment hash"""
        request = ln.PaymentHash(r_hash_str=r_hash_str)
        response = self.stub.LookupInvoice(request)
        return response

    def list_payments(self):
        """List all outgoing payments"""
        request = ln.ListPaymentsRequest()
        response = self.stub.ListPayments(request)
        return response

    def describe_graph(self):
        """Describe the network graph"""
        request = ln.ChannelGraphRequest()
        response = self.stub.DescribeGraph(request)
        return response

    def get_channel_info(self, channel_id):
        """Get the state of a specific channel"""
        requset = ln.ChanInfoRequest(chan_id=channel_id)
        response = self.stub.GetChanInfo(requset)
        return response

    def get_node_info(self, pub_key):
        """Get information on a specific node"""
        request = ln.NodeInfoRequest(pub_key=pub_key)
        response = self.stub.GetNodeInfo(request)
        return response

    def query_routes(self, pub_key, amt, num_routes=5):
        """Query a route to a destination"""
        request = ln.QueryRoutesRequest(pub_key=pub_key, amt=amt, num_routes=num_routes)
        response = self.stub.QueryRoutes(request)
        return response

    def get_network_info(self):
        """Returns basic stats about the known channel graph for this node"""
        request = ln.NetworkInfoRequest()
        response = self.stub.GetNetworkInfo(request)
        return response

    def decode_payment_request(self, payment_request):
        """Decode a payment request"""
        request = ln.PayReqString(payment_request)
        response = self.stub.DecodePayReq(request)
        return response

    def list_transactions(self):
        """List on chain transactions from the wallet"""
        request = ln.GetTransactionsRequest()
        response = self.stub.GetTransactions(request)
        return response

    def stop_daemon(self):
        """Stop and shutdown the daemon"""
        request = ln.StopRequest()
        response = self.stub.StopDaemon(request)
        return response

    def sign_message(self, msg):
        """Sign a message with the node's private key"""
        request = ln.SignMessageRequest(msg=msg)
        response = self.stub.SignMessage(request)
        return response

    def verify_message(self, msg, signature):
        """Verify a message signed with the signature"""
        request = ln.VerifyMessageRequest(msg=msg, signature=signature)
        response = self.stub.VerifyMessage(request)
        return response

    def fee_report(self):
        """Display the current fee policies of all active channels"""
        request = ln.FeeReportRequest()
        response = self.stub.FeeReport(request)
        return response

    def update_channel_policy(self, base_fee_msat=None, fee_rate=None, time_lock_delta=None,
                              channel_point=None, all_channels=False):
        """Update the channel policy for all channels, or a single channel"""
        kwargs = {
            'global': all_channels
        }
        if base_fee_msat:
            kwargs['base_fee_msat'] = base_fee_msat
        if fee_rate:
            kwargs['fee_rate'] = fee_rate
        if channel_point:
            kwargs['channel_point'] = channel_point
        if time_lock_delta:
            kwargs['time_lock_delta'] = time_lock_delta

        request = ln.PolicyUpdateRequest(**kwargs)
        response = self.stub.UpdateChannelPolicy(request)
        return response

    def send_on_chain_many(self, address_amount_map, sat_ber_byte=None, target_conf=None):
        """Send bitcoin on-chain to multiple addresses"""
        pass  # TODO

    def send_on_chain(self, address, amount, sat_ber_byte=None, target_conf=None):
        """Send bitcoin on-chain to a single address"""
        optional_kwargs = {}
        if sat_ber_byte is not None:
            optional_kwargs['sat_ber_byte'] = sat_ber_byte
        if target_conf is not None:
            optional_kwargs['target_conf'] = target_conf

        request = ln.SendCoinsRequest(addr=address, amount=amount, **optional_kwargs)
        response = self.stub.SendCoins(request)
        return response


class AsyncRPCClient:

    def __init__(self, ip_address, cert=None, macaroon=None):
        if cert is None:
            cert = get_cert()
        else:
            cert = cert

        if macaroon is None:
            macaroon = get_macaroon()
        else:
            macaroon = macaroon

        credentials = generate_credentials(cert, macaroon)
        ip_address = 'ipv4:///' + ip_address
        channel = aiogrpc.secure_channel(ip_address, credentials)
        self.stub = lnrpc.LightningStub(channel)

    async def get_info(self):
        response = await self.stub.GetInfo(ln.GetInfoRequest())
        return response

    async def wallet_balance(self):
        response = await self.stub.WalletBalance(ln.WalletBalanceRequest())
        return response

    async def channel_balance(self):
        response = await self.stub.ChannelBalance(ln.ChannelBalanceRequest())
        return response

    async def list_peers(self):
        """List all active, currently connected peers"""
        response = await self.stub.ListPeers(ln.ListPeersRequest())
        return response

    async def list_channels(self):
        """List all open channels"""
        response = await self.stub.ListChannels(ln.ListChannelsRequest())
        return response

    async def open_channel(self, node_pubkey, local_funding_amount=None, push_sat=None, private=False):
        """Open a channel to an existing peer"""
        request = ln.OpenChannelRequest(
            node_pubkey=node_pubkey,
            local_funding_amount=local_funding_amount,
            push_sat=push_sat,
            private=private
        )
        response = await self.stub.OpenChannel(request)
        return response

    async def list_invoices(self):
        request = ln.ListInvoiceRequest()
        response = await self.stub.ListInvoices(request)
        return response

    async def subscribe_invoices(self):
        async for invoice in self.stub.SubscribeInvoices(ln.InvoiceSubscription()):
            yield invoice

    async def add_invoice(self, value, memo=''):
        request = ln.Invoice(value=value, memo=memo)
        response = await self.stub.AddInvoice(request)
        return response

    async def unlock(self, password):
        """Unlock encrypted wallet at lnd startup"""
        pass  # TODO

    async def new_address(self):
        """Generates a new witness address"""
        request = ln.NewWitnessAddressRequest()
        response = await self.stub.NewWitnessAddress(request)
        return response

    async def connect_peer(self, ln_address, permanent=False):
        """Connect to a remote lnd peer"""
        request = ln.ConnectPeerRequest(addr=ln_address, perm=permanent)
        response = await self.stub.ConnectPeer(request)
        return response

    async def disconnect_peer(self, pub_key):
        """Disconnect a remote lnd peer identified by public key"""
        request = ln.DisconnectPeerRequest(pub_key=pub_key)
        response = await self.stub.DisconnectPeer(request)
        return response

    async def close_channel(self, channel_point, force=False, target_conf=None, sat_per_byte=None):
        """Close an existing channel"""
        request = ln.CloseChannelRequest(
            channel_point=channel_point,
            force=force,
            target_conf=target_conf,
            sat_per_byte=sat_per_byte
        )
        response = await self.stub.CloseChannel(request)
        return response

    async def pending_channels(self):
        """Display information pertaining to pending channels"""
        request = ln.PendingChannelsRequest()
        response = await self.stub.PendingChannels(request)
        return response

    async def send_payment(self, payment_request):
        """Send a payment over lightning"""
        request = ln.SendRequest(payment_request=payment_request)
        response = await self.stub.SendPaymentSync(request)
        return response

    async def lookup_invoice(self, r_hash_str):
        """Lookup an existing invoice by its payment hash"""
        request = ln.PaymentHash(r_hash_str=r_hash_str)
        response = await self.stub.LookupInvoice(request)
        return response

    async def list_payments(self):
        """List all outgoing payments"""
        request = ln.ListPaymentsRequest()
        response = await self.stub.ListPayments(request)
        return response

    async def describe_graph(self):
        """Describe the network graph"""
        request = ln.ChannelGraphRequest()
        response = await self.stub.DescribeGraph(request)
        return response

    async def get_channel_info(self, channel_id):
        """Get the state of a specific channel"""
        requset = ln.ChanInfoRequest(chan_id=channel_id)
        response = await self.stub.GetChanInfo(requset)
        return response

    async def get_node_info(self, pub_key):
        """Get information on a specific node"""
        request = ln.NodeInfoRequest(pub_key=pub_key)
        response = await self.stub.GetNodeInfo(request)
        return response

    async def query_routes(self, pub_key, amt, num_routes=5):
        """Query a route to a destination"""
        request = ln.QueryRoutesRequest(pub_key=pub_key, amt=amt, num_routes=num_routes)
        response = await self.stub.QueryRoutes(request)
        return response

    async def get_network_info(self):
        """Returns basic stats about the known channel graph for this node"""
        request = ln.NetworkInfoRequest()
        response = await self.stub.GetNetworkInfo(request)
        return response

    async def decode_payment_request(self, payment_request):
        """Decode a payment request"""
        request = ln.PayReqString(payment_request)
        response = await self.stub.DecodePayReq(request)
        return response

    async def list_transactions(self):
        """List on chain transactions from the wallet"""
        request = ln.GetTransactionsRequest()
        response = await self.stub.GetTransactions(request)
        return response

    async def stop_daemon(self):
        """Stop and shutdown the daemon"""
        request = ln.StopRequest()
        response = await self.stub.StopDaemon(request)
        return response

    async def sign_message(self, msg):
        """Sign a message with the node's private key"""
        request = ln.SignMessageRequest(msg=msg)
        response = await self.stub.SignMessage(request)
        return response

    async def verify_message(self, msg, signature):
        """Verify a message signed with the signature"""
        request = ln.VerifyMessageRequest(msg=msg, signature=signature)
        response = await self.stub.VerifyMessage(request)
        return response

    async def fee_report(self):
        """Display the current fee policies of all active channels"""
        request = ln.FeeReportRequest()
        response = await self.stub.FeeReport(request)
        return response

    async def update_channel_policy(self, base_fee_msat=None, fee_rate=None, time_lock_delta=None,
                                    channel_point=None, all_channels=False):
        """Update the channel policy for all channels, or a single channel"""
        pass  # TODO

    async def send_on_chain(self, address, amount, sat_ber_byte=None, target_conf=None):
        """Send bitcoin on-chain to a single address"""
        optional_kwargs = {}
        if sat_ber_byte is not None:
            optional_kwargs['sat_ber_byte'] = sat_ber_byte
        if target_conf is not None:
            optional_kwargs['target_conf'] = target_conf

        request = ln.SendCoinsRequest(addr=address, amount=amount, **optional_kwargs)
        response = await self.stub.SendCoins(request)
        return response
