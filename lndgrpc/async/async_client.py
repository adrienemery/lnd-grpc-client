import sys
from lndgrpc.common import get_cert, get_macaroon, generate_credentials, ln, lnrpc

MAJOR = sys.version_info[0]
MINOR = sys.version_info[1]

if MAJOR == 3 and MINOR >= 5:
    import aiogrpc

    class AsyncLNDClient(object):

        def __init__(self, ip_address, cert=None, cert_filepath=None, macaroon=None, macaroon_filepath=None):
            if cert is None:
                cert = get_cert(cert_filepath)

            if macaroon is None:
                macaroon = get_macaroon(macaroon_filepath)

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
            await self.stub.SubscribeInvoices(ln.InvoiceSubscription())

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
