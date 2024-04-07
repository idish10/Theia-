from bfxapi import Client
import sys
import asyncio
from collections import OrderedDict
from dotenv import load_dotenv
from pattrn_robust_tracking.loggers.bitfinex.util import *
from pattrn_robust_tracking.loggers.exchange import Exchange
import ccxt
import os
import time
import csv

load_dotenv()
sys.path.append("../../../")

HOUR = 3600000


class BitfinexTrader(Exchange):
    def __init__(self, key: str, secret: str, is_sandbox: bool):
        super().__init__(key, secret)
        self.trader = ccxt.bitfinex2(
            {
                "apiKey": "O6cOJTPfVtwY3pvLwQgqDFxz29mVPPEph1vVgvQbBGb",
                "secret": "nAr2SQADxfIVIYgMH2BswyLRvA6lYpWFVl0GQXiQ41M",
            }
        )
        self.trader.set_sandbox_mode(is_sandbox)
        self.movments = Client(
            API_KEY=self.key,
            API_SECRET=self.secret,
            logLevel="DEBUG",
        )

    async def get_price_by_timestamp(self, symbol, trade_time):
        price_per_time_table = await self.movments.rest.get_seed_candles(
            symbol,
            start=trade_time,
            end=trade_time + HOUR / 2,
            sort=1,
        )
        # get the currency price per time
        avg_price_per_time = (
            price_per_time_table[0][1] + price_per_time_table[0][2]
        ) / 2
        return avg_price_per_time

    def get_trades(self):
        """
        Return your trades from day one into a sorted list by time stamp
        """
        trades = []
        loop = True
        starter_time = 0

        while loop:
            temp_trades = self.trader.fetch_my_trades(
                symbol=None, since=starter_time, limit=50, params={"sort": 1}
            )

            if len(temp_trades) == 0 or starter_time == temp_trades[-1]["timestamp"]:
                return list(
                    OrderedDict([(trade["id"], trade) for trade in trades]).values()
                )
            trades += list(temp_trades)
            starter_time = int(temp_trades[-1]["timestamp"])

    async def trade_to_csv(self, trades):
        """building a csv file from list of trades
        Args:
            trades (list): iterate over trades and pulling info to csv file
        """
        with open("csv_files/trades.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "#",
                    "Order ID",
                    "Pair",
                    "Amount",
                    "Total Price in USD",
                    "Fee in USD",
                    "Date",
                ]
            )
            for trade in trades:
                amount = float(trade["info"][4])
                trade_time = float(trade["timestamp"])
                gmt = time.gmtime(trade["timestamp"] / 1000)
                tmstr = "{0}.{1}.{2}".format(gmt.tm_mday, gmt.tm_mon, gmt.tm_year)
                fee = float(trade["fee"]["cost"])
                temp_str = trade["symbol"]
                index_pos = temp_str.find("/")
                left_coin = temp_str[0:index_pos:]
                right_coin = temp_str[index_pos + 1 : :]

                # TODO - implemeting EURO case
                if right_coin == "EUR":
                    right_coin = "USD"
                total_price = trade["price"] * trade["amount"]

                if left_coin == "LUNC":
                    continue

                if right_coin != "USD" and right_coin != "USDT":
                    if amount < 0:
                        right_pair = to_symbol(right_coin)
                        avg = await self.get_price_by_timestamp(right_pair, trade_time)
                        total_price *= avg
                        fee = "{:.3f}".format(float(trade["fee"]["cost"]) * avg)
                    else:
                        right_pair = to_symbol(right_coin)
                        avg = await self.get_price_by_timestamp(right_pair, trade_time)
                        total_price *= avg
                        left_pair = to_symbol(left_coin)
                        avg = await self.get_price_by_timestamp(left_pair, trade_time)
                        fee = "{:.3f}".format(float(trade["fee"]["cost"]) * avg)
                else:
                    if amount > 0 and left_coin != "USDT":
                        left_pair = to_symbol(left_coin)
                        avg = await self.get_price_by_timestamp(left_pair, trade_time)
                        fee = "{:.3f}".format(float(trade["fee"]["cost"]) * avg)

                writer.writerow(
                    [
                        trade["id"],
                        trade["order"],
                        trade["symbol"],
                        "{:.3f}".format(amount),
                        "{:.3f}".format(total_price),
                        "{:.3f}".format(float(fee)),
                        tmstr,
                    ]
                )
        return

    async def get_movments(self):
        """this funcion get all the movments from bitfinex acc
        Returns:
        list of momvents:
        """
        deposits = []
        withdrawals = []
        latest_timestamp = 0
        last_transaction_id = ""

        while True:
            raw_transactions = self.trader.fetch_transactions(
                since=latest_timestamp, limit=250, params={"sort": 1}
            )

            if last_transaction_id == raw_transactions[-1]["id"]:
                break

            last_transaction_id = raw_transactions[-1]["id"]
            latest_timestamp = raw_transactions[-1]["timestamp"]

            #
            for transaction_data in raw_transactions:
                transaction_data: dict

                if transaction_data["amount"] > 0:
                    deposits.append(
                        transaction_data
                    )  # Warning, transaction data may not be equivilent to movement.__dict__
                else:
                    withdrawals.append(transaction_data)  # Same goes here

        return deposits, withdrawals

    async def movement_to_csv(self, movments, type):
        path = f"csv_files/{type}.csv"
        with open(path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Withdrawl/Deposit",
                    "Currency",
                    "Amount",
                    "Total price in USD",
                    "Fee in USD",
                    "Date",
                ]
            )
            for move in movments:
                gmt = time.gmtime(move["date"].timestamp())
                date = "{0}.{1}.{2}".format(gmt.tm_mday, gmt.tm_mon, gmt.tm_year)
                amount = abs(float(move["amount"]))
                currency = to_symbol(move["currency"])
                ticker = await self.get_price_by_timestamp(
                    currency, move["mts_started"]
                )
                total_value_in_usd = amount * ticker
                fees = abs(float(move["fees"])) * ticker

                writer.writerow(
                    [
                        type,
                        move["currency"],
                        "{:.3f}".format(amount),
                        "{:.3f}".format(total_value_in_usd),
                        "{:.3f}".format(fees),
                        date,
                    ]
                )


async def run():
    trader = BitfinexTrader(
        "jahbEU5k8ckhMZieYMyrnD9rxZRMkNFfGQzDtVHVQiE",
        "k0negnSqUDyfJURrojq9w8RfKj2KSr25HIxpfxu4PgW",
        False,
    )
    deposits, withdrawls = await trader.get_movments()
    trades = trader.get_trades()
    # await trader.movement_to_csv(deposits, type="deposit")
    # await trader.movement_to_csv(withdrawls, type="withdrawl")
    # await trader.trade_to_csv(trades)


if __name__ == "__main__":
    runner = asyncio.ensure_future(run())
    asyncio.get_event_loop().run_until_complete(runner)
