import pytest
import grpc
from lndgrpc.client import LNDClient


@pytest.fixture
def client():
    client = LNDClient(admin=False, network='simnet')
    return client


@pytest.fixture
def admin_client():
    client = LNDClient('127.0.0.1:10009', admin=True, network='simnet')
    return client


def test_init():
    """Ensure we can create a client with no errors"""
    LNDClient(network='simnet')


def test_get_info(client):
    response = client.get_info()
    assert hasattr(response, 'identity_pubkey')


def test_wallet_balance(client):
    client.wallet_balance()


def test_channel_balance(client):
    client.channel_balance()


def test_list_peers(client):
    client.list_peers()


def test_list_invoices(client):
    client.list_invoices()


def tests_add_invoice_fail_read_only(client):
    # the default macaroon is readonly and thus should
    # not be able to create invoices
    with pytest.raises(grpc.RpcError):
        client.add_invoice(200, 'test')


def tests_add_invoice(admin_client):
    admin_client.add_invoice(200, 'test')


def test_new_address(admin_client):
    admin_client.new_address()


def test_pending_channels(client):
    client.pending_channels()

