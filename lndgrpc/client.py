from .common import ln, BaseClient
from .errors import handle_rpc_errors


class LNDClient(BaseClient):

    def unlock(self, password):
        """Unlock encrypted wallet at lnd startup"""
        request = ln.UnlockWalletRequest(wallet_password=password.encode())
        response = self._wallet_stub.UnlockWallet(request)
        return response

    def init_wallet(self):
        raise NotImplementedError

    def generate_seed(self):
        raise NotImplementedError

    @handle_rpc_errors
    def get_info(self):
        response = self._ln_stub.GetInfo(ln.GetInfoRequest())
        return response

    @handle_rpc_errors
    def wallet_balance(self):
        response = self._ln_stub.WalletBalance(ln.WalletBalanceRequest())
        return response

    @handle_rpc_errors
    def channel_balance(self):
        response = self._ln_stub.ChannelBalance(ln.ChannelBalanceRequest())
        return response

    @handle_rpc_errors
    def list_peers(self):
        """List all active, currently connected peers"""
        response = self._ln_stub.ListPeers(ln.ListPeersRequest())
        return response

    @handle_rpc_errors
    def list_channels(self):
        """List all open channels"""
        response = self._ln_stub.ListChannels(ln.ListChannelsRequest())
        return response

    @handle_rpc_errors
    def open_channel(self, node_pubkey, local_funding_amount=None, push_sat=None, private=False):
        """Open a channel to an existing peer"""
        request = ln.OpenChannelRequest(
            node_pubkey_string=node_pubkey,
            local_funding_amount=local_funding_amount,
            push_sat=push_sat,
            private=private
        )
        response = self._ln_stub.OpenChannel(request)
        return response

    @handle_rpc_errors
    def list_invoices(self):
        request = ln.ListInvoiceRequest()
        response = self._ln_stub.ListInvoices(request)
        return response

    @handle_rpc_errors
    def subscribe_invoices(self):
        for invoice in self._ln_stub.SubscribeInvoices(ln.InvoiceSubscription()):
            yield invoice

    @handle_rpc_errors
    def add_invoice(self, value, memo=''):
        request = ln.Invoice(value=value, memo=memo)
        response = self._ln_stub.AddInvoice(request)
        return response

    @handle_rpc_errors
    def new_address(self):
        """Generates a new witness address"""
        request = ln.NewWitnessAddressRequest()
        response = self._ln_stub.NewWitnessAddress(request)
        return response

    @handle_rpc_errors
    def connect_peer(self, pub_key, host, permanent=False):
        """Connect to a remote lnd peer"""
        ln_address = ln.LightningAddress(pubkey=pub_key, host=host)
        request = ln.ConnectPeerRequest(addr=ln_address, perm=permanent)
        response = self._ln_stub.ConnectPeer(request)
        return response

    @handle_rpc_errors
    def disconnect_peer(self, pub_key):
        """Disconnect a remote lnd peer identified by public key"""
        request = ln.DisconnectPeerRequest(pub_key=pub_key)
        response = self._ln_stub.DisconnectPeer(request)
        return response

    @handle_rpc_errors
    def close_channel(self, channel_point, force=False, target_conf=None, sat_per_byte=None):
        """Close an existing channel"""
        funding_txid, output_index = channel_point.split(':')
        channel_point = ln.ChannelPoint(
            funding_txid_str=funding_txid,
            output_index=int(output_index)
        )
        request = ln.CloseChannelRequest(
            channel_point=channel_point,
            force=force,
            target_conf=target_conf,
            sat_per_byte=sat_per_byte
        )
        response = self._ln_stub.CloseChannel(request)
        return response

    @handle_rpc_errors
    def pending_channels(self):
        """Display information pertaining to pending channels"""
        request = ln.PendingChannelsRequest()
        response = self._ln_stub.PendingChannels(request)
        return response

    @handle_rpc_errors
    def send_payment(self, payment_request):
        """Send a payment over lightning"""
        request = ln.SendRequest(payment_request=payment_request)
        response = self._ln_stub.SendPaymentSync(request)
        return response

    @handle_rpc_errors
    def lookup_invoice(self, r_hash_str):
        """Lookup an existing invoice by its payment hash"""
        request = ln.PaymentHash(r_hash_str=r_hash_str)
        response = self._ln_stub.LookupInvoice(request)
        return response

    @handle_rpc_errors
    def list_payments(self):
        """List all outgoing payments"""
        request = ln.ListPaymentsRequest()
        response = self._ln_stub.ListPayments(request)
        return response

    @handle_rpc_errors
    def describe_graph(self):
        """Describe the network graph"""
        request = ln.ChannelGraphRequest()
        response = self._ln_stub.DescribeGraph(request)
        return response

    @handle_rpc_errors
    def get_channel_info(self, channel_id):
        """Get the state of a specific channel"""
        requset = ln.ChanInfoRequest(chan_id=channel_id)
        response = self._ln_stub.GetChanInfo(requset)
        return response

    @handle_rpc_errors
    def get_node_info(self, pub_key):
        """Get information on a specific node"""
        request = ln.NodeInfoRequest(pub_key=pub_key)
        response = self._ln_stub.GetNodeInfo(request)
        return response

    @handle_rpc_errors
    def query_routes(self, pub_key, amt, num_routes=5):
        """Query a route to a destination"""
        request = ln.QueryRoutesRequest(pub_key=pub_key, amt=amt, num_routes=num_routes)
        response = self._ln_stub.QueryRoutes(request)
        return response

    @handle_rpc_errors
    def get_network_info(self):
        """Returns basic stats about the known channel graph for this node"""
        request = ln.NetworkInfoRequest()
        response = self._ln_stub.GetNetworkInfo(request)
        return response

    @handle_rpc_errors
    def decode_payment_request(self, payment_request):
        """Decode a payment request"""
        request = ln.PayReqString(pay_req=payment_request)
        response = self._ln_stub.DecodePayReq(request)
        return response

    @handle_rpc_errors
    def list_transactions(self):
        """List on chain transactions from the wallet"""
        request = ln.GetTransactionsRequest()
        response = self._ln_stub.GetTransactions(request)
        return response

    @handle_rpc_errors
    def stop_daemon(self):
        """Stop and shutdown the daemon"""
        request = ln.StopRequest()
        response = self._ln_stub.StopDaemon(request)
        return response

    @handle_rpc_errors
    def sign_message(self, msg):
        """Sign a message with the node's private key"""
        request = ln.SignMessageRequest(msg=msg)
        response = self._ln_stub.SignMessage(request)
        return response

    @handle_rpc_errors
    def verify_message(self, msg, signature):
        """Verify a message signed with the signature"""
        request = ln.VerifyMessageRequest(msg=msg, signature=signature)
        response = self._ln_stub.VerifyMessage(request)
        return response

    @handle_rpc_errors
    def fee_report(self):
        """Display the current fee policies of all active channels"""
        request = ln.FeeReportRequest()
        response = self._ln_stub.FeeReport(request)
        return response

    @handle_rpc_errors
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
        response = self._ln_stub.UpdateChannelPolicy(request)
        return response

    @handle_rpc_errors
    def send_on_chain_many(self, address_amount_map, sat_ber_byte=None, target_conf=None):
        """Send bitcoin on-chain to multiple addresses"""
        pass  # TODO

    @handle_rpc_errors
    def send_on_chain(self, address, amount, sat_ber_byte=None, target_conf=None):
        """Send bitcoin on-chain to a single address"""
        optional_kwargs = {}
        if sat_ber_byte is not None:
            optional_kwargs['sat_ber_byte'] = sat_ber_byte
        if target_conf is not None:
            optional_kwargs['target_conf'] = target_conf

        request = ln.SendCoinsRequest(addr=address, amount=amount, **optional_kwargs)
        response = self._ln_stub.SendCoins(request)
        return response
