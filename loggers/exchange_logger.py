from decimal import Decimal
import requests
import os
import pattrn_robust_tracking.manager.db.mongo_for_theia as prtm


class ExchangeLogger:
    def __init__(self, client: str, key: str, secret: str, mongo_conn: str):
        self.client = client
        self.key = key
        self.secret = secret
        self.mongo_conn = mongo_conn

    def log_balance(self):
        raise NotImplementedError("Please Implement this method")

    def debug_print(self, wallet_type: str, balance: int, tokens: dict) -> None:

        print(f"hey {self.client} your token balance is changed to {balance} ")
        for symbol in tokens:
            symb = str(symbol).lower()
            token_count, token_usd_value = tokens[symbol]
            print(
                f"{self.client} your {wallet_type} account have been updated your {symb} balance have been changed to : {'{:.10f}'.format(token_count)}"
            )
            print(
                f"{self.client} your {wallet_type} account have been updated your {symb} usd_balance have been changed to : {'{:.10f}'.format(token_usd_value)}"
            )

    def write(
        self,
        venue_name: str,
        inner_wallet_name: str,
        balance: int,
        tokens: dict,
        debug=False,
    ) -> int:
        """
        Write reporting data to Mongo Cloud
        """
        if debug:
            self.debug_print(venue_name, balance, tokens)
            return
        else:
            mdb_client = prtm.MongoParser(self.mongo_conn)
            mdb_client.update_log(venue_name, self.client, balance, inner_wallet_name)
            for symbol in tokens:
                symb = str(symbol).lower()
                token_count, token_usd_value = tokens[symbol]
                mdb_client.update_token_log(
                    venue_name,
                    self.client,
                    token_count,
                    token_usd_value,
                    symb,
                    inner_wallet_name,
                )

            return balance
