from pattrn_robust_tracking.loggers.exchange import Exchange
from ccxt.kucoin import kucoin
from kucoin.user import user
import time


STARTRING_TRADING_DATE = 1600000000000
WEEK = 604800000


class KucoinTrader(Exchange):
    def __init__(self, key: str, secret: str, api_passphrase: str, is_sandbox: bool):
        super().__init__(key, secret)
        self.ccxt_trader = kucoin(
            {
                "password": api_passphrase,
                "apiKey": key,
                "secret": secret,
            }
        )
        self.ccxt_trader.set_sandbox_mode(is_sandbox)
        self.user = user.UserData(key, secret, api_passphrase, is_sandbox)

    def get_trades(self, type, tradeType="spot"):
        """
        fetching trades from kucoin
        you can fetch only the trades that happend in the last 7 days="WEEK"
        unless you send @starter_time and iterate through time
        Args:
             type can be market or limit
             tradeType can be spot trading or margin trading deafult is spot trading
        Returns:
            list:  trades
        """
        trades = []
        temp_trades = []
        starter_time = STARTRING_TRADING_DATE
        while starter_time < int(time.time()) * 1000:
            try:

                temp_trades = self.ccxt_trader.fetch_my_trades(
                    symbol=None,
                    since=starter_time,
                    limit=50,
                    params={"sort": 1, "type": type, "tradeType": tradeType},
                )
            except Exception as e:
                msg = str(e)
                # code:200002 is rate limit indicator
                if '"code":"200002"' in msg:
                    time.sleep(10)

            if len(temp_trades) == 0:
                starter_time += WEEK
                continue
            trades += list(temp_trades)
            starter_time = int(temp_trades[-1]["timestamp"]) + 1

        return trades

    def get_deposits(self):
        """
        get all acc's deposits
        iterate through all pages with  currentPage argument


        Returns:
            _type_: _description_
        """

        deposit_list = []
        counter = 1
        while True:
            temp_deposit_list = self.user.get_deposit_list(currentPage=counter)
            if len(temp_deposit_list["items"]) == 0:
                break
            deposit_list.append(temp_deposit_list["items"])
            counter += 1
            if counter > temp_deposit_list["totalPage"]:
                deposit_list = sum(deposit_list, [])
                deposit_list.reverse()
                break

        return deposit_list

    def get_withdrawls(self):
        """
        get all acc's withdrawls
        iterate through all pages with  currentPage argument


        Returns:
            _type_: _description_
        """

        withdrawal_list = []
        counter = 1
        while True:
            temp_withdrawal_list = self.user.get_withdrawal_list(currentPage=counter)
            if len(temp_withdrawal_list["items"]) == 0:
                break
            withdrawal_list.append(temp_withdrawal_list["items"])
            counter += 1
            if counter > temp_withdrawal_list["totalPage"]:
                withdrawal_list = sum(withdrawal_list, [])
                withdrawal_list.reverse()
                break

        return withdrawal_list


if __name__ == "__main__":
    trader = KucoinTrader(
        key="63270bdfc3987600012addab",
        secret="43f32d81-a0e3-4a56-90f3-f1d3a02981b8",
        api_passphrase="KDht37hwyv",
        is_sandbox=False,
    )
