from binance.spot import Spot
from binance.um_futures import UMFutures
import os
from pattrn_robust_tracking.loggers.exchange_logger import ExchangeLogger
from pattrn_robust_tracking.utils.util import coralogix_decorator


class BinanceLogger(ExchangeLogger):
    def __init__(self, client: str, key: str, secret: str, mongo_conn: str):
        super().__init__(client, key, secret, mongo_conn)
        self.binance_client = Spot(key=key, secret=secret)
        self.binance_future_client = UMFutures(key=key, secret=secret)

    def get_ticker_price(self, symbol: str):
        if symbol == "USDT":
            return 1.0
        return float(self.binance_client.ticker_price(symbol=f"{symbol}USDT")["price"])

    def get_spot_balances(self):

        usd_balance = 0
        all_pairs = self.binance_client.account()
        all_pairs = [all for all in all_pairs["balances"] if float(all["free"]) != 0.0]
        aggregated_pairs = {}
        for item in all_pairs:

            asset_value = float(item["free"]) + float(item["locked"])
            asset_value_usd = self.get_ticker_price(symbol=item["asset"]) * asset_value
            usd_balance += asset_value_usd
            if item["asset"] not in aggregated_pairs:
                aggregated_pairs[item["asset"]] = [asset_value, asset_value_usd]

            else:
                aggregated_pairs[item["asset"]][0] += asset_value
                aggregated_pairs[item["asset"]][1] += asset_value_usd

        return usd_balance, aggregated_pairs

    def get_futures_balances(self):
        usd_balance = 0
        future_balances = {}
        all_assets = self.binance_future_client.balance()
        for asset in all_assets:
            if float(asset["balance"]) != 0:

                asset_value = float(asset["balance"])
                asset_value_usd = (
                    self.get_ticker_price(symbol=asset["asset"]) * asset_value
                )
                usd_balance += asset_value_usd
                if asset["asset"] not in future_balances:
                    future_balances[asset["asset"]] = [asset_value, asset_value_usd]
                else:
                    future_balances[asset["asset"]][0] += asset_value
                    future_balances[asset["asset"]][1] += asset_value_usd

        return (
            usd_balance,
            future_balances,
        )

    def log_balance(self):
        balance_from_spot, tokens_from_spot = self.get_spot_balances()
        balance_from_futures, tokens_from_futures = self.get_futures_balances()
        self.write(
            venue_name="Binance",
            inner_wallet_name="SPOT",
            balance=balance_from_spot,
            tokens=tokens_from_spot,
        )
        self.write(
            venue_name="Binance",
            inner_wallet_name="FUTURES",
            balance=balance_from_futures,
            tokens=tokens_from_futures,
        )
        return balance_from_futures + balance_from_spot


@coralogix_decorator(client=os.environ["CLIENT"], wallet_type="binance")
def main():

    return BinanceLogger(
        client=os.environ["CLIENT"],
        key=os.environ["KEY"],
        secret=os.environ["SECRET"],
        mongo_conn=os.environ["MONGO_CONN"],
    ).log_balance()

    # return BinanceLogger(
    #     key="m3QLJ1fFK4QTJm9cfXitxFrGnIs30Gl7m2w5UPo9BmphojbKChZwffRH3M2o9Own",
    #     secret="1MoHTRkI4e8GukZeB5kWNfGRiGdB87MtAP6TVtVqnRlqqiOhfI00nCaj85Qe0qVQ",
    #     client="ziv",
    #     mongo_conn="mongodb+srv://pattrn:pattrn1234@cluster0.ydhsz.mongodb.net/PortfolioTracking?retryWrites=true&w=majority",
    # ).log_balance()


if __name__ == "__main__":
    main()
