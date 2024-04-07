from pattrn_robust_tracking.loggers.exchange import Exchange
from pattrn_robust_tracking.loggers.binance.utils import *
import time
import ccxt.binance
from binance.client import Client


NINETY_DAYS = 7776000000
STARTRING_TRADING_DATE = 1573571914000


class BinanceSpotTrader(Exchange):

    multiplier_waiting_time = 1

    def __init__(self, key: str, secret: str, is_sandbox: bool):
        super().__init__(key, secret)
        self.trader = ccxt.binance(
            {
                "apiKey": key,
                "secret": secret,
            }
        )
        self.trader.set_sandbox_mode(is_sandbox)

        self.movments = Client(api_key=key, api_secret=secret)

    def get_trades(self):
        """iterate through the oldest trade timestamp
        Args:
          update_pairs - fetch_my_trade requires a symbol as mandatoy to query thier api
          update_pairs is the relevant symbol list

        Returns:
            _type_: _description_
        """
        update_pairs = relevant_symbol(self.movments)
        trades = []
        start = 0
        for sym in update_pairs:

            while True:

                try:
                    while True:
                        temp_trades = self.trader.fetch_my_trades(
                            symbol=sym,
                            limit=1000,
                            params={"startTime": start, "type": "spot"},
                        )
                        if len(temp_trades) == 0:
                            start = 0
                            break
                        trades += temp_trades

                        start = int(temp_trades[-1]["info"]["time"]) + 1
                    break

                except Exception as e:
                    handling_rate_limit_exception(
                        e, BinanceSpotTrader.multiplier_waiting_time
                    )
                    BinanceSpotTrader.multiplier_waiting_time += 1

        return sorted(trades, key=sort_by_time)

    def get_withdrawls(self):
        """_summary_
        Please notice the default startTime and endTime to make sure that time interval is within 0-90 days.
        If both startTime and endTime are sent, time between startTime and endTime must be less than 90 days
        this method trying to catch the newst withdraw every iterate otherwise adding 90 days to startTime and endTime
        Returns:
            _type_: _description_
        """

        withdrawls = []
        start = STARTRING_TRADING_DATE
        end = start + NINETY_DAYS
        today = time.time() * 1000
        rate_limit = True
        while end < today:

            temp_start = start
            while rate_limit:
                try:
                    temp_withdrawls = self.movments.get_withdraw_history(
                        startTime=start, endTime=end, limit=50, status=6
                    )
                    rate_limit = False

                except Exception as e:
                    handling_rate_limit_exception(e)
                    BinanceSpotTrader.multiplier_waiting_time += 1

            for withs in temp_withdrawls:
                withdrawls.append(withs)
                with_time = date_to_seconds(withs["applyTime"]) * 1000
                if with_time > start:
                    start = with_time

            if temp_start == start:
                start += NINETY_DAYS
            end = start + NINETY_DAYS
            rate_limit = True

        return sorted(withdrawls, key=sort_by_apply_time_key)

    def get_deposits(self):
        """_summary_
        Please notice the default startTime and endTime to make sure that time interval is within 0-90 days.
        If both startTime and endTime are sent, time between startTime and endTime must be less than 90 days
        this method trying to catch the newst deposit every iterate otherwise we adding 90 days to startTime and endTime
        Returns:
            _type_: _description_
        """
        deposits = []
        start = STARTRING_TRADING_DATE
        end = start + NINETY_DAYS
        today = int(time.time()) * 1000
        rate_limit = True
        while end < today + NINETY_DAYS:
            temp_start = start
            while rate_limit:
                try:
                    temp_deposits = self.movments.get_deposit_history(
                        startTime=start, endTime=end, limit=50, status=1
                    )
                    rate_limit = False

                except Exception as e:
                    handling_rate_limit_exception(e)
                    BinanceSpotTrader.multiplier_waiting_time += 1

            for dep in temp_deposits:
                deposits.append(dep)
                dep_time = dep["insertTime"]
                if dep_time > start:
                    start = dep_time + 1
            if temp_start == start:
                start += NINETY_DAYS
            end = start + NINETY_DAYS
            rate_limit = True

        return sorted(deposits, key=sort_by_insert_time_key)


if __name__ == "__main__":
    trader = BinanceSpotTrader(
        key="gA49JR5bOU6U6MXzOb780moGJVRenEchMkODvRpSbp7C0sbvWlKJ8rN1KITxNnwZ",
        secret="5O2jlwXJSFcloATDKEeEoI5GItx1GyTg5SkOjh5ax6QfawnySmz03aUnDWofZql8",
        is_sandbox=False,
    )
