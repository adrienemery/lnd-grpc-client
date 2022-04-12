import sys
from lndgrpc.common import invoices, ln, BaseClient
from lndgrpc.errors import handle_rpc_errors

MAJOR = sys.version_info[0]
MINOR = sys.version_info[1]


# only python 3.6+ is supported by aiogrpc
if MAJOR == 3 and MINOR >= 6:
    import aiogrpc

    class AsyncLNDClient(BaseClient):
        grpc_module = aiogrpc

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ip_address = 'ipv4:///' + self.ip_address

        @handle_rpc_errors
        async def get_info(self):
            response = await self._ln_stub.GetInfo(ln.GetInfoRequest())
            return response

        @handle_rpc_errors
        async def wallet_balance(self):
            response = await self._ln_stub.WalletBalance(ln.WalletBalanceRequest())
            return response

        @handle_rpc_errors
        async def channel_balance(self):
            response = await self._ln_stub.ChannelBalance(ln.ChannelBalanceRequest())
            return response

        @handle_rpc_errors
        async def list_peers(self):
            """List all active, currently connected peers"""
            response = await self._ln_stub.ListPeers(ln.ListPeersRequest())
            return response

        @handle_rpc_errors
        async def list_channels(self):
            """List all open channels"""
            response = await self._ln_stub.ListChannels(ln.ListChannelsRequest())
            return response

        @handle_rpc_errors
        async def open_channel(self, node_pubkey, local_funding_amount=None, push_sat=None, private=False):
            """Open a channel to an existing peer"""
            request = ln.OpenChannelRequest(
                node_pubkey_string=node_pubkey,
                local_funding_amount=local_funding_amount,
                push_sat=push_sat,
                private=private
            )
            response = await self._ln_stub.OpenChannel(request)
            return response

        @handle_rpc_errors
        async def list_invoices(self):
            request = ln.ListInvoiceRequest()
            response = await self._ln_stub.ListInvoices(request)
            return response

        @handle_rpc_errors
        async def subscribe_invoices(self):
            async for invoice in self._ln_stub.SubscribeInvoices(
                ln.InvoiceSubscription()
            ):
                yield invoice

        @handle_rpc_errors
        async def subscribe_single_invoice(self, r_hash):
            request = ln.PaymentHash(r_hash=r_hash)
            async for invoice in self._invoices_stub.SubscribeSingleInvoice(
                request
            ):
                yield invoice

        @handle_rpc_errors
        async def add_invoice(self, value, memo=''):
            request = ln.Invoice(value=value, memo=memo)
            response = await self._ln_stub.AddInvoice(request)
            return response

        @handle_rpc_errors
        async def add_hold_invoice(self, hash, value=0, memo=''):
            request = invoices.AddHoldInvoiceRequest(
                hash=hash, value=value, memo=memo)
            response = await self._invoices_stub.AddHoldInvoice(request)
            return response

        @handle_rpc_errors
        async def settle_invoice(self, preimage):
            request = invoices.SettleInvoiceMsg(preimage=preimage)
            response = await self._invoices_stub.SettleInvoice(request)
            return response

        @handle_rpc_errors
        async def cancel_invoice(self, payment_hash):
            request = invoices.CancelInvoiceMsg(payment_hash=payment_hash)
            response = await self._invoices_stub.CancelInvoice(request)
            return response

        @handle_rpc_errors
        async def unlock(self, password):
            """Unlock encrypted wallet at lnd startup"""
            request = ln.UnlockWalletRequest(wallet_password=password.encode())
            response = await self._wallet_stub.UnlockWallet(request)
            return response

        @handle_rpc_errors
        async def new_address(self, address_type=0):
            """Generates a new witness address"""
            request = ln.NewAddressRequest(type=address_type)
            response = await self._ln_stub.NewAddress(request)
            return response

        @handle_rpc_errors
        async def connect_peer(self, pub_key, host, permanent=False):
            """Connect to a remote lnd peer"""
            ln_address = ln.LightningAddress(pubkey=pub_key, host=host)
            request = ln.ConnectPeerRequest(addr=ln_address, perm=permanent)
            response = await self._ln_stub.ConnectPeer(request)
            return response

        @handle_rpc_errors
        async def disconnect_peer(self, pub_key):
            """Disconnect a remote lnd peer identified by public key"""
            request = ln.DisconnectPeerRequest(pub_key=pub_key)
            response = await self._ln_stub.DisconnectPeer(request)
            return response

        @handle_rpc_errors
        async def close_channel(self, channel_point, force=False, target_conf=None, sat_per_byte=None):
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
            response = await self._ln_stub.CloseChannel(request)
            return response

        @handle_rpc_errors
        async def pending_channels(self):
            """Display information pertaining to pending channels"""
            request = ln.PendingChannelsRequest()
            response = await self._ln_stub.PendingChannels(request)
            return response

        @handle_rpc_errors
        async def send_payment(self, payment_request):
            """Send a payment over lightning"""
            request = ln.SendRequest(payment_request=payment_request)
            response = await self._ln_stub.SendPaymentSync(request)
            return response

        @handle_rpc_errors
        async def lookup_invoice(self, r_hash_str):
            """Lookup an existing invoice by its payment hash"""
            request = ln.PaymentHash(r_hash_str=r_hash_str)
            response = await self._ln_stub.LookupInvoice(request)
            return response

        @handle_rpc_errors
        async def list_payments(self):
            """List all outgoing payments"""
            request = ln.ListPaymentsRequest()
            response = await self._ln_stub.ListPayments(request)
            return response

        @handle_rpc_errors
        async def describe_graph(self):
            """Describe the network graph"""
            request = ln.ChannelGraphRequest()
            response = await self._ln_stub.DescribeGraph(request)
            return response

        @handle_rpc_errors
        async def get_channel_info(self, channel_id):
            """Get the state of a specific channel"""
            requset = ln.ChanInfoRequest(chan_id=channel_id)
            response = await self._ln_stub.GetChanInfo(requset)
            return response

        @handle_rpc_errors
        async def get_node_info(self, pub_key):
            """Get information on a specific node"""
            request = ln.NodeInfoRequest(pub_key=pub_key)
            response = await self._ln_stub.GetNodeInfo(request)
            return response

        @handle_rpc_errors
        async def query_routes(self, pub_key, amt, num_routes=5):
            """Query a route to a destination"""
            request = ln.QueryRoutesRequest(pub_key=pub_key, amt=amt, num_routes=num_routes)
            response = await self._ln_stub.QueryRoutes(request)
            return response

        @handle_rpc_errors
        async def get_network_info(self):
            """Returns basic stats about the known channel graph for this node"""
            request = ln.NetworkInfoRequest()
            response = await self._ln_stub.GetNetworkInfo(request)
            return response

        @handle_rpc_errors
        async def decode_payment_request(self, payment_request):
            """Decode a payment request"""
            request = ln.PayReqString(pay_req=payment_request)
            response = await self._ln_stub.DecodePayReq(request)
            return response

        @handle_rpc_errors
        async def list_transactions(self):
            """List on chain transactions from the wallet"""
            request = ln.GetTransactionsRequest()
            response = await self._ln_stub.GetTransactions(request)
            return response

        @handle_rpc_errors
        async def stop_daemon(self):
            """Stop and shutdown the daemon"""
            request = ln.StopRequest()
            response = await self._ln_stub.StopDaemon(request)
            return response

        @handle_rpc_errors
        async def sign_message(self, msg):
            """Sign a message with the node's private key"""
            request = ln.SignMessageRequest(msg=msg)
            response = await self._ln_stub.SignMessage(request)
            return response

        @handle_rpc_errors
        async def verify_message(self, msg, signature):
            """Verify a message signed with the signature"""
            request = ln.VerifyMessageRequest(msg=msg, signature=signature)
            response = await self._ln_stub.VerifyMessage(request)
            return response

        @handle_rpc_errors
        async def fee_report(self):
            """Display the current fee policies of all active channels"""
            request = ln.FeeReportRequest()
            response = await self._ln_stub.FeeReport(request)
            return response

        @handle_rpc_errors
        async def update_channel_policy(self, base_fee_msat=None, fee_rate=None, time_lock_delta=None,
                                        channel_point=None, all_channels=False):
            """Update the channel policy for all channels, or a single channel"""
            pass  # TODO

        @handle_rpc_errors
        async def send_on_chain(self, address, amount, sat_ber_byte=None, target_conf=None):
            """Send bitcoin on-chain to a single address"""
            optional_kwargs = {}
            if sat_ber_byte is not None:
                optional_kwargs['sat_ber_byte'] = sat_ber_byte
            if target_conf is not None:
                optional_kwargs['target_conf'] = target_conf

            request = ln.SendCoinsRequest(addr=address, amount=amount, **optional_kwargs)
            response = await self._ln_stub.SendCoins(request)
            return response
