import requests
import json
import subprocess as sp
import time
from functools import wraps
from decimal import Decimal
from collections import Counter
from pattrn_robust_tracking.loggers.wallet_logger import WalletLogger
# from pattrn_robust_tracking.utils.util import coralogix_decorator

"""
    These first few variables are inaccurate and probably need fixing / find a different solution
"""
OSMOSISD = "./osmosisd-6.4.0-linux-amd64"
QUERY_LP_SHARE = "query gamm total-share"
REQUIRED_PARAMS = (
    "--output=json   --node https://rpc.osmosis.interbloc.org:443 --chain-id osmosis-1"
)


IMPERATOR_QUERY_POOL = "https://api-osmosis.imperator.co/pools/v2/{}"
IMPERATOR_QUERY_TOKEN_PRICE = "https://api-osmosis.imperator.co/tokens/v2/price/{}"
IMPERATOR_DENOM_TO_SYMBOL = "https://api-osmosis.imperator.co/search/v1/symbol?denom={}"


def retry(times):
    """retry a function a number of times"""

    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    result = fn(*args, **kwargs)
                    break
                except Exception as e:
                    time.sleep(3)
            return result
        return wrapper
    return decorate


@retry(times=10)
def get_symbol(denom):
    print("Symbol")
    return requests.get(IMPERATOR_DENOM_TO_SYMBOL.format(denom)).json()["symbol"]


@retry(times=10)
def get_current_prices(symbol):
    print("Price")
    return requests.get(IMPERATOR_QUERY_TOKEN_PRICE.format(symbol)).json()["price"]


@retry(times=10)
def get_pool_data(pool_num):
    print("Pool")
    return requests.get(IMPERATOR_QUERY_POOL.format(pool_num)).json()


class OsmoLogger(WalletLogger):
    def __init__(self, wallet_address, client_name, mongo_conn):
        super().__init__(wallet_address, client_name, mongo_conn)

    def get_osmosis_balances(self):
        if 'osmo' in self.wallet_address:
            self.wallet_type = 'osmosis'
        if 'cosmos' in self.wallet_address:
            self.wallet_type = 'cosmoshub'
        if 'juno' in self.wallet_address:
            self.wallet_type = 'juno'
        if 'evmos' in self.wallet_address:
            self.wallet_type = 'evmos'
            
        # TODO - Move to osmosisd
        balances = Counter()
        osmosis_balances = requests.get(
            f"https://lcd-{self.wallet_type}.keplr.app/bank/balances/{self.wallet_address}"
        ).json()

        for balance in osmosis_balances["result"]:
            try:
                if str(balance["denom"]).startswith("gamm/pool/"):
                    pool_num = balance["denom"].split("/")[-1]
                    pool_data = get_pool_data(pool_num)
                    pool_share = self.get_pool_share(balance, pool_num)
                    for asset in pool_data:
                        symbol = asset["symbol"]
                        balances[symbol] += Decimal(asset["amount"]) * pool_share
                else:
                    # The denom we recieve contains a 'u' or 'a' at the beggining of the symbol and so we remove it (uosmo, ujuno)
                    symbol = balance["denom"][1:].upper()
                    balances[symbol] += Decimal(balance["amount"]) / 1_000_000
            except Exception as e:
                # TODO: Implement error reporting
                pass
        return balances

    def get_pool_share(self, pool, pool_num):
        query_total_share = "{0} {1} {2} {3}".format(
            OSMOSISD, QUERY_LP_SHARE, pool_num, REQUIRED_PARAMS
        )
        total_share = json.loads(
            sp.run(
                [query_total_share], capture_output=True, text=True, shell=True
            ).stdout
        )
        pool_share = float(pool["amount"]) / float(total_share["totalShares"]["amount"])
        return Decimal(pool_share)

    def log_osmo_balance(self):
        token_amounts = self.get_osmosis_balances()
        total_usd_balance = 0
        token_values = {}
        
        # Besides the wallet holding we need to calculate the delegations invested in
        delegations = requests.get(f"https://{self.wallet_type}.stakesystems.io/cosmos/staking/v1beta1/delegations/{self.wallet_address}").json()['delegation_responses']
        if delegations != []:
            for delegation in delegations:
                denom = delegation['balance']['denom'][1:].upper()
                token_amounts[denom] += Decimal(delegation['balance']['amount']) / 1_000_000
        delegation_rewards = requests.get(f"https://{self.wallet_type}.stakesystems.io/cosmos/distribution/v1beta1/delegators/{self.wallet_address}/rewards").json()['total']
        if delegation_rewards != []:
            denom = delegation['balance']['denom'][1:].upper()
            token_amounts[denom] += Decimal(delegation_rewards[0]['amount']) / 1_000_000    
        # You might want to add for validator accounts a calculation of the commission they get
        for symbol in token_amounts:
            # Only temporary there are some symbol which the code dosen't recognize and for now we skip them
            if symbol == '':
                continue
            token_usd_value = float(get_current_prices(symbol))
            # USD value of each token you have in your wallet (includes delegations and staking rewards)
            token_values[symbol] = float(token_amounts[symbol]) * float(token_usd_value)
            total_usd_balance += float(token_amounts[symbol]) * token_usd_value

        print(f"Total USD balance: {total_usd_balance}")
        
        
        """
            I temporarily disabled the mongo and coralogix logging   <----   IMPORTANT
        """
        # field_name = f"{self.client_name}_total_osmo_balance"
        # self.write(self.client_name, field_name, tot_osmo)

        # for symbol in token_values:
        #     field_name = f"token_{self.client_name}_{symbol}_balance"
        #     self.write(
        #         self.client_name,
        #         field_name,
        #         token_values[symbol],
        #         token_count=True,
        #         wallet_type="osmo",
        #         token=symbol,
        #     )
        return total_usd_balance

        # self.remove_sold_tokens("osmo", self.client_name, token_values)


# @coralogix_decorator(client=os.environ["CLIENT"], wallet_type="osmo")
def main():
    
    # OsmoLogger(os.environ['ADDRESS'], os.environ['CLIENT'],
    #            os.environ['MONGO_CONN']).log_osmo_balance()
    return OsmoLogger(
        "osmo1zf4eut8kwnz4zulfrnns26rg8k3888mdvc5qy4",
        "ziv",
        "mongodb+srv://pattrn:pattrn1234@cluster0.ydhsz.mongodb.net/PortfolioTracking?retryWrites=true&w=majority",
    ).log_osmo_balance()


if __name__ == "__main__":
    main()