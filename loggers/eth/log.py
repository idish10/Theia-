from pattrn_robust_tracking.loggers.wallet_logger import WalletLogger
from decimal import Decimal
import requests
import time as tm
import os
from pattrn_robust_tracking.utils.wallets import Wallets
from pattrn_robust_tracking.utils.util import coralogix_decorator

import logging

# from coralogix.handlers import CoralogixLogger  # For version 2.x and above.
# from pattrn_robust_tracking.utils.util import coralogix_decorator


class EthLogger(WalletLogger):
    def __init__(self, wallet_address, client_name, mongo_conn):
        super().__init__(wallet_address, client_name, mongo_conn)
        self.wallet = Wallets("ethereum")

    def get_eth_wallet_balances(self):
        balances = {}
        data = requests.get(
            f"https://api.ethplorer.io/getAddressInfo/{self.wallet_address}?apiKey=freekey"
        ).json()
        balances["ethereum"] = Decimal(data["ETH"]["balance"])
        for token in data.get("tokens", []):
            balances[token["tokenInfo"]["address"]] = Decimal(
                token["rawBalance"]
            ) / 10 ** int(token["tokenInfo"]["decimals"])
        return balances

    # def get_eth_balance(self):
    #     wallet_balances = self.get_eth_wallet_balances()
    #     balance = {}
    #     total_usd_balance = 0

    #     for symbol in wallet_balances:

    #         symbol_upper = str(symbol).upper()
    #         token_usd_balance = float(wallet_balances[symbol]) * \
    #             float(self.get_current_prices([symbol_upper])[symbol_upper])
    #         balance[symbol] = token_usd_balance
    #         total_usd_balance += token_usd_balance

    #     print(f"Loggin: {balance} {total_usd_balance}")
    #     return balance, total_usd_balance

    def get_eth_balance(self):
        wallet_balances = self.get_eth_wallet_balances()
        balance = {}
        total_usd_balance = 0

        for symbol in wallet_balances:
            if symbol == "ethereum":
                price = self.wallet.llama_pricing(symbol, tm.time(), coingecko=True)
            else:
                price = self.wallet.llama_pricing(symbol, tm.time())
            if price is not None:
                token_usd_balance = float(wallet_balances[symbol]) * float(price)
                # token_usd_balance = float(wallet_balances[symbol]) * \
                #     float(get_current_prices([symbol_upper])[symbol_upper])

                if symbol not in balance:
                    balance[symbol] = (
                        token_usd_balance,
                        float(wallet_balances[symbol]),
                    )

                total_usd_balance += token_usd_balance

        return balance, total_usd_balance

    def merge_values(self, log_dict):
        usd_keys = set(log_dict.get("USD", {}).keys())
        token_keys = set(log_dict.get("token", {}).keys())
        common_keys = usd_keys & token_keys

        result = {}
        for key in common_keys:
            usd_value = log_dict.get("USD", {}).get(key)
            token_value = log_dict.get("token", {}).get(key)
            result[key] = (usd_value, token_value)

        return result

    def log_balance(self):
        balances, total_usd_balance = self.get_eth_balance()
        # balances = self.merge_values(balance)

        # field_name = f"{self.client_name}_total_eth_balance"
        # self.write(self.client_name, field_name, total_eth_balance)

        self.write(self.client_name, balances, total_usd_balance)

        return total_usd_balance


def main():
    # return EthLogger(
    #     "0x95Ab5E9554CA6F8b6B0f65B13E39E76Bf4082851",
    #     "ziv",
    #     "mongodb+srv://pattrn:pattrn1234@cluster0.ydhsz.mongodb.net/PortfolioTracking?retryWrites=true&w=majority",
    # ).log_balance()
    return EthLogger(
        os.environ["ADDRESS"], os.environ["CLIENT"], os.environ["MONGO_CONN"]
    ).log_balance()


if __name__ == "__main__":
    main()
