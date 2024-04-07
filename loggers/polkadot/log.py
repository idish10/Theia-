import requests
from web3 import Web3, HTTPProvider
from pattrn_robust_tracking.utils.wallets import Wallets
from pattrn_robust_tracking.utils.constants import PROVIDERS


def get_account_transfers(acc_address):
    wallet = Wallets(wallet_type="polkadot")
    transactions = wallet.get_polkadot_transaction(1, acc_address)
    print(len(transactions["data"]["transfers"]))


get_account_transfers(acc_address="13P4g7ZWKCqkWJC9HbdnUj2Kcgeo5YfcHCHgAcL722BJwdnd")
