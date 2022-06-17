from .common import invoices, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class InvoicesRPC(BaseClient):
    # INVOICES
    @handle_rpc_errors
    def subscribe_single_invoice(self, r_hash):
        """Subscribe to state of a single invoice"""
        request = invoices.SubscribeSingleInvoiceRequest(r_hash=r_hash)
        response = self._invoices_stub.SubscribeSingleInvoice(request)
        for first in response:
            return first

    #Open Batch Channels
    @handle_rpc_errors
    def batch_open_channel(self,channels, sat_per_vbyte, label ,**kwargs):
        """BatchOpenChannel attempts to open multiple single-funded channels in a single transaction in an atomic way."""
        #Convert Channel Pubkey into bytes
        for channel in channels:
            channel['node_pubkey']=bytes.fromhex(channel['node_pubkey'])

        request = ln.BatchOpenChannelRequest(
            channels=channels,
            sat_per_vbyte=sat_per_vbyte,
            label=label,
            **kwargs
            )

        response =  self._ln_stub.BatchOpenChannel(request)

        return response.pending_channels
