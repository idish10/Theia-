from bfxapi import Client
import logging
import asyncio
import os

from pattrn_robust_tracking.utils.util import coralogix_decorator
from pattrn_robust_tracking.loggers.exchange_logger import ExchangeLogger


class BitfinexLogger(ExchangeLogger):
    def __init__(self, client, key, secret, mongo_conn):
        super().__init__(client, key, secret, mongo_conn)

    async def get_margin_balance(self, key, secret):
        bc = Client(API_KEY=key, API_SECRET=secret, logLevel="DEBUG")
        wallets = await bc.rest.get_wallets()
        margin_balance = [e for e in wallets if e.type == "margin"]
        bfx_balance = 0
        tokens = {}
        for margin in margin_balance:
            coin = margin.currency
            if coin == "USD":
                bfx_balance += margin.balance
                continue
            text = BitfinexLogger.to_pair(coin)
            token_price = await bc.rest.get_public_ticker(text)
            bfx_balance += token_price[0] * margin.balance
            if coin in tokens:
                tokens[coin][0] += margin.balance
                tokens[coin][1] += token_price[0] * margin.balance
            else:
                tokens[coin] = [margin.balance, token_price[0] * margin.balance]

        return bfx_balance, tokens

    @classmethod
    def to_pair(cls, coin):
        if len(coin) == 3:
            return "t{}USD".format(coin)
        else:
            return "t{}:USD".format(coin)

    async def get_total_balance(self, key, secret):
        bc = Client(API_KEY=key, API_SECRET=secret, logLevel="DEBUG")
        wallets = await bc.rest.get_wallets()
        wallets = [w for w in wallets if w.type == "exchange"]
        bfx_balance = 0
        tokens = {}

        for wallet in wallets:
            coin = wallet.currency

            if coin == "USD":
                bfx_balance += wallet.balance
                continue

            text = BitfinexLogger.to_pair(coin)

            token_price = await bc.rest.get_public_ticker(text)
            bfx_balance += token_price[0] * wallet.balance

            if coin in tokens:
                tokens[coin][0] += wallet.balance
                tokens[coin][1] += token_price[0] * wallet.balance
            else:
                tokens[coin] = [wallet.balance, token_price[0] * wallet.balance]

        return bfx_balance, tokens

    async def get_bitfinex_balance(self, key, secret):

        tokens_from_spot = {}

        tokens_from_margin = {}
        balance_from_margin, tokens_from_margin = await self.get_margin_balance(
            key, secret
        )
        balance_from_spot, tokens_from_spot = await self.get_total_balance(key, secret)
        return (
            balance_from_spot,
            balance_from_margin,
            tokens_from_spot,
            tokens_from_margin,
        )

    def log_balance(self):
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(self.get_bitfinex_balance(self.key, self.secret))
        (
            balance_from_spot,
            balance_from_margin,
            tokens_from_spot,
            tokens_from_margin,
        ) = loop.run_until_complete(task)
        print(f"BFX SPOT balance: {balance_from_spot}")
        print(f"BFX MARGIN balance: {balance_from_margin}")

        self.write("Bitfinex", "SPOT", balance_from_spot, tokens_from_spot, debug=False)
        self.write(
            "Bitfinex",
            "MARGIN",
            balance_from_margin,
            tokens_from_margin,
            debug=False,
        )

        return balance_from_spot + balance_from_margin


@coralogix_decorator(client="ziv", wallet_type="bitfinex")
def main():

    return BitfinexLogger(
        client=os.environ["CLIENT"],
        key=os.environ["KEY"],
        secret=os.environ["SECRET"],
        mongo_conn=os.environ["MONGO_CONN"],
    ).log_balance()

    # return BitfinexLogger(
    #     "ziv",
    #     "O6cOJTPfVtwY3pvLwQgqDFxz29mVPPEph1vVgvQbBGb",
    #     "nAr2SQADxfIVIYgMH2BswyLRvA6lYpWFVl0GQXiQ41M",
    #     "mongodb+srv://pattrn:pattrn1234@cluster0.ydhsz.mongodb.net/PortfolioTracking?retryWrites=true&w=majority",
    # ).log_balance()


if __name__ == "__main__":
    main()
