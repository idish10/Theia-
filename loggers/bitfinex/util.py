import csv
import time


HOUR = 3600000


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


async def get_price_by_timestamp(self, symbol, trade_time):
    price_per_time_table = await self.movments.rest.get_seed_candles(
        symbol,
        start=trade_time,
        end=trade_time + HOUR / 2,
        sort=1,
    )
    # get the currency price per time
    avg_price_per_time = (price_per_time_table[0][1] + price_per_time_table[0][2]) / 2
    return avg_price_per_time


def to_symbol(coin):
    if len(coin) == 3:
        pair = "t" + coin + "USD"
    else:
        pair = "t" + coin + ":" + "USD"
    return pair
