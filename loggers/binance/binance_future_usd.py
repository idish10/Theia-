from binance.um_futures import UMFutures
from pattrn_robust_tracking.loggers.binance.utils import *
from pattrn_robust_tracking.loggers.exchange import Exchange


SEVEN_DAYS = 604800000


class BinanceFuturesUsd(Exchange):
    multiplier_waiting_time = 1

    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.um_futures_client = UMFutures(key=self.key, secret=self.secret)

    def get_trades(self, start=1638712442000):
        """
        fetching our trades from USDT-M wallet
        the method assume the first trade was conducted at 5.12.2021
        seven days is the maximum range for this method and every request are limited to 1000 trades



        """

        end = start + SEVEN_DAYS
        rate_limit = True
        today = int(time.time() * 1000)
        transaction_hist = []
        temp = None
        while end - SEVEN_DAYS < today:
            while rate_limit:
                try:
                    temp = self.um_futures_client.get_income_history(
                        limit=1000, startTime=start, endTime=end
                    )
                    rate_limit = False

                except Exception as e:
                    handling_rate_limit_exception(
                        e, BinanceFuturesUsd.multiplier_waiting_time
                    )
                    BinanceFuturesUsd.multiplier_waiting_time += 1

                finally:
                    # if rate_limit==False thats indicate that we succefuly communicate with the api
                    if rate_limit == False:
                        if len(temp) == 1000:
                            # that indicate that we have more or equal than 1000 trades, than we update our range properly
                            start = int(temp[-1]["time"]) + 1
                        else:

                            start = end
                        end = start + SEVEN_DAYS

            if len(temp) != 0:
                transaction_hist += temp
                temp = None
            rate_limit = True

        return transaction_hist


if __name__ == "__main__":
    object = BinanceFuturesUsd(
        key="7ugMIRgle3KjF5miuUmZasQxuvFflQF6Ug5SGm0ZC4LMCPhQcVhoyT1RD0r5NGP1",
        secret="TVe1IQeipydy51todQbnmu4fQSt7loICb4LgqzOYKcBdsByIEKU1QYdWTX6hkQPd",
    )
    print(object.get_trades())
