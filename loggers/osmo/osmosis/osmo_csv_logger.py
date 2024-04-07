from pattrn_robust_tracking.loggers.osmo.osmosis import api_data
import math
import csv
import time
import datetime
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.common.Exporter import Exporter
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.common.localconfig import config
from pattrn_robust_tracking.utils.wallets import Wallets
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.common.ibc.handle import (
    handle_unknown_detect_transfers,
)
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.common.ibc.processor import (
    txinfo,
    handle_message,
)
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.common.ibc.api_rpc import (
    get_txs_all as rpc_api,
)
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.common.ibc.api_lcd import (
    get_txs_all as lcd_api,
)
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.settings_csv import (
    EVMOS_NODE,
    NGM_NODE,
    OSMO_NODE,
    AKASH_NODE,
    SCRT_NODE,
    KAVA_NODE,
    DVPN_LCD_NODE,
    SOM_NODE,
    TICKER_EVMOS,
    MINTSCAN_LABEL,
)
from pattrn_robust_tracking.utils.constants import *
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.common import report_util


def _read_options(options):
    """Currently not in use its used for the osmosis logger"""
    report_util.read_common_options(config, options)
    print("localconfig: {}", config.__dict__)


def _pages(wallet_address):
    """Returns list of page numbers to be retrieved e.g. [1,0]"""
    max_txs = 30000
    num_txs = min(api_data.get_count_txs(wallet_address), max_txs)

    last_page = math.ceil(num_txs / api_data.LIMIT_PER_QUERY) - 1
    pages = list(range(last_page, -1, -1))
    return pages


def _remove_dups(elems, txids_seen):
    """API data has duplicate transaction data, this function removes them"""
    out = []
    for elem in elems:
        txid = elem["txhash"]
        if txid in txids_seen:
            continue

        out.append(elem)
        txids_seen.add(txid)

    return out


def _fetch_and_process_txs(wallet_address, pages):

    """This Transaction list fetcher is currently in uses for only osmo logger

    Returns:
        list: Contains the transaction list before processing
    """

    # Fetch and parse data in batches (cumulative required too much memory), oldest first.
    # Note: oldest first is opposite of api default (allows simpler lp stake/unstake logic)
    transaction_list = []
    txids_seen = set()
    i = 0
    for page in pages:
        i += 1
        elems = api_data.get_txs(wallet_address, page * api_data.LIMIT_PER_QUERY)

        # Remove duplicates (data from this api has duplicates)
        elems_clean = _remove_dups(elems, txids_seen)

        # Sort to process oldest first (so that lock/unlock tokens transactions processed correctly)
        elems_clean.sort(key=lambda elem: elem["timestamp"])
        transaction_list += elems_clean
    return transaction_list


def _process_txs(wallet_address, elems, exporter, ticker):
    """
    This goes over the different transactions (elems=transactions) and handles each transaction seperately
    """
    for elem in elems:
        process_tx(wallet_address, elem, exporter, ticker)


def process_tx(wallet_address, elem, exporter, ticker):
    """This function activates message handlers for each transaction found in the transaction list
       It processes the transaction by their messages/types upon recieving a transaction it may be a transfer/deposit/adding liquidity and so on
       and each of those actions has a different type or message that is represented in the returned json file inside elem (the var) and each different
       action usually comes with unique transaction format for the needed data and the handlers found in staketaxcsv/common/ibc/processor.py which also use functions
       found in staketaxcsv/common/ibc/handle.py which are the different handlers for each transaction message. (***read the Returns***)

    Args:
        wallet_address (string): The person's wallet address
        elem (dict): Contains the unprocessed transaction info
        exporter (Exporter): Handles the transaction and sorts it by our needs
        ticker (string): This describes the current blockchain e.g. Evmos,Osmosis

    Returns:
        TxInfoIBC: This return isn't necessary, the actual returned item is the edited exporter variable which actually contains the changes (exporter.rows())
    """
    tx_info = txinfo(wallet_address, elem, MINTSCAN_LABEL[ticker], {}, EVMOS_NODE)
    for msginfo in tx_info.msgs:
        result = handle_message(exporter, tx_info, msginfo, config.debug)
        if result:
            continue

        handle_unknown_detect_transfers(exporter, tx_info, msginfo)

    return tx_info


def run(wallet_address, node, ticker):
    """This function conducts the background activations that are needed in order to get and process the transactions

    Args:
        wallet_address (string): The person's wallet address
        node (string): Describes the provider node we use
        ticker (string): This describes the current blockchain e.g. Evmos,Osmosis

    Returns:
        Exporter: The handler of the trades, the actual transactions are founded in exporter.rows()
    """
    elems = lcd_api(node, wallet_address)
    exporter = Exporter(wallet_address, None, ticker)
    _process_txs(wallet_address, elems, exporter, ticker)
    return exporter


def date_to_sec(date):
    index_pos = date.find("-")
    year = date[0:index_pos:]
    temp_str = date[index_pos + 1 : :]
    index_pos = temp_str.find("-")
    month = temp_str[0:index_pos:]
    day = temp_str[index_pos + 1 : :]
    index_pos = day.find(" ")
    day = day[0:index_pos]
    date = day + "/" + month + "/" + year
    return time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())


def exporter_to_csv(exporter):
    with open(f"/home/idan/Desktop/evmos_transactions.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(RUNNING_SELL_HEADER)
        for trade in exporter.rows:
            if trade.sent_amount != "":
                side = "SELL"
                sym = trade.sent_currency
                amount = trade.sent_amount
            else:
                side = "BUY"
                sym = trade.received_currency
                amount = trade.received_amount
            fee = trade.fee
            date = date_to_sec(trade.timestamp)
            wallet = Wallets("evmos")
            price = wallet.get_price_gecko(name="evmos", sym="evmos", timestamp=date)
            date = time.asctime(time.localtime(date))
            writer.writerow(
                [
                    side,
                    sym,
                    f"{float(price) * float(amount):.8f}",
                    f"{float(amount):.8f}",
                    f"{float(price):.8f}",
                    f"{float(fee) * float(price):.8f}",
                    date,
                ]
            )


if __name__ == "__main__":
    wallet_address = "evmos1h4ttma4g297suu9atnwd7h2ke78t4skgjjcpzd"
    # TODO need to make the calls dynamic meaning change the node,ticker variables to be dependant on a string which describes the chain
    exporter = run(wallet_address, EVMOS_NODE, TICKER_EVMOS)
    # BreakPoint <-------- Here to understand the contents of exporter.rows()
    exporter_to_csv(exporter)
    """
        This currently works when conducted on evmos,scrt,akash,sommlier,emoney,sentinel with no difficult processing
        Osmosis need more extended processing
    """

    """
        Also for reference there may be some files or functions not in use i will remove them soon.
    """
