from .common import walletunlocker, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class WalletUnlockerRPC(BaseClient):
    #WALLETUNLOCKERRPC
    def unlock(self, password):
        """Unlock encrypted wallet at lnd startup"""
        request = ln.UnlockWalletRequest(wallet_password=password.encode())
        response = self._wallet_stub.UnlockWallet(request)
        return response

    def init_wallet(self, **kwargs):
        request = walletunlocker.InitWalletRequest(**kwargs)
        response = self._walletunlocker_stub.InitWallet(request)
        return response

    def gen_seed(self, aezeed_passphrase, seed_entropy):
        request = walletunlocker.GenSeedRequest(
            aezeed_passphrase=aezeed_passphrase,
            seed_entropy=seed_entropy
        )
        response = self._walletunlocker_stub.GenSeed(request)
        return response

    def change_password(self, current_password, new_password, stateless_init, new_macaroon_root_key):
        request = walletunlocker.ChangePasswordRequest(
            current_password=current_password,
            new_password=new_password,
            stateless_init=stateless_init,
            new_macaroon_root_key=new_macaroon_root_key
        )
        response = self._walletunlocker_stub.ChangePassword(request)
        return response
    
    @handle_rpc_errors
    def unlock_wallet(self, **kwargs):
        request = walletunlocker.UnlockWalletRequest(**kwargs)
        try:
            response = self._walletunlocker_stub.UnlockWallet(request)
            return response
        except Exception as e:
            print(e)
            print("Wallet might already be unlocked")