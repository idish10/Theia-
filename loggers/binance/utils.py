import datetime
import dateparser
import pytz
import time


def get_coins_from_spot(client):
    """
    get all assets from Fiat and Spot wallet
    float(all["free"]) != 0.0 indicate that token have value on account

    Returns:
        _type_: _description_
    """

    all_pairs = client.get_account()
    all_pairs = [
        all["asset"] for all in all_pairs["balances"] if float(all["free"]) != 0.0
    ]

    return all_pairs


def get_all_pairs_from_binance(client):
    """
    get all the pairs from binance

    Returns:
        _type_: _description_
    """
    all = client.get_all_tickers()
    temp = [all["symbol"] for all in all]
    return set(temp)


def cartesian_product(coins_list_from_spot):
    """
    creating new list of active pairs from spot trading market


    Args:
        coins_list_from_spot (_type_): _description_

    Returns:
        _type_: _description_
    """
    filterd_coins_list = []
    for index, coin in enumerate(coins_list_from_spot):
        for ind, coi in enumerate(coins_list_from_spot):
            if index != ind:
                filterd_coins_list.append(coin + coi)
    return set(filterd_coins_list)


def relevant_symbol(client):
    # intersection beteween the pairs from trading spot to all the coin from binance
    symbols_from_spot = get_coins_from_spot(client)
    cartesian_symbols = cartesian_product(symbols_from_spot)
    all_pairs = get_all_pairs_from_binance(client)
    return cartesian_symbols.intersection(all_pairs)


def sort_by_time(trades_list):
    return trades_list["info"]["time"]


def sort_by_insert_time_key(dct):
    return dct["insertTime"] // 1000


def sort_by_apply_time_key(dct):
    return date_to_seconds(dct["applyTime"])


def handling_rate_limit_exception(excep: Exception, multiplier_waiting_time: int):
    msg = str(excep)
    if "code=-1003" in msg:
        time.sleep(60 * multiplier_waiting_time)


def date_to_seconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds())
