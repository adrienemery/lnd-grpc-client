from .common import invoices, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class InvoicesRPC(BaseClient):
    @handle_rpc_errors
    def subscribe_single_invoice(self, r_hash):
        """Subscribe to state of a single invoice"""
        request = invoices.SubscribeSingleInvoiceRequest(r_hash=r_hash)
        response = self._invoices_stub.SubscribeSingleInvoice(request)
        for first in response:
            return first

    @handle_rpc_errors
    def cancel_invoice(self, payment_hash):
        """CancelInvoice"""
        request = invoices.CancelInvoiceMsg(payment_hash=payment_hash)
        response = self._invoices_stub.CancelInvoice(request)
        return response

    @handle_rpc_errors
    def lookup_invoice_v2(self, payment_hash=None, payment_addr=None, set_id=None, lookup_modifier=None):
        """LookupInvoiceV2"""
        LookupInvoiceMsg
        LookupInvoiceV2
        request = invoices.LookupInvoiceMsg(
            payment_hash=payment_hash,
            payment_addr=payment_addr,
            set_id=set_id,
            lookup_modifier=lookup_modifier
        )
        response = self._invoices_stub.LookupInvoiceV2(request)
        return response

    @handle_rpc_errors
    def settle_invoice(self, r_hash):
        """SettleInvoice"""
        # SettleInvoiceMsg
        # SettleInvoice
        pass

    @handle_rpc_errors
    def settle_invoice(self, r_hash):
        """AddHoldInvoice"""
        # AddHoldInvoiceRequest
        # AddHoldInvoice
        pass

