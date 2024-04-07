from decimal import Decimal
import requests
import os
import pattrn_robust_tracking.manager.db.mongo_for_theia as prtm

CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
OSMO_URL = "https://api-osmosis.imperator.co/tokens/v1/all"


class WalletLogger(object):
    def __init__(self, wallet_address: str, client_name: str, mongo_conn: str):
        self.wallet_address = wallet_address
        self.client_name = client_name
        self.mongo_conn = mongo_conn

    def log_balance(self):
        raise NotImplementedError("Please Implement this method")

    def debug_print(
        self,
        client_name: str,
        field_name: str,
        balance: int,
        token_count=False,
        wallet_type="",
        token="",
    ) -> None:
        if token_count:
            print(f"hey {client_name} your token balance is changed to {balance} ")
        else:
            print(f"hey {client_name} your balance is changed to {balance} ")

    def write(
        self,
        client_name: str,
        balance,
        total_eth_balance: int,
        debug=False,
    ):
        """
        Write reporting data to Mongo Cloud
        """
        if debug:
            self.debug_print(client_name, balance, total_eth_balance)
            return
        mdb_client = prtm.MongoParser(self.mongo_conn)
        mdb_client.update_log("Eth", client_name, total_eth_balance, "")
        for symbol in balance:
            symb = str(symbol).lower()
            token_usd_value, token_count = balance[symbol]
            mdb_client.update_token_log(
                "Eth", client_name, token_count, token_usd_value, symb, ""
            )
