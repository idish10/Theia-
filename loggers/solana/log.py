import requests as req
import json
from pattrn_robust_tracking.utils.wallets import Wallets
from decimal import Decimal
import time as tm
from pattrn_robust_tracking.utils.constants import *
import csv


def spl_transfers(wallet_address, uni_test):
    count = 0
    # At first we want to get the first 10 SPL transfers where wallet_address is the refferenced address and offset is our starting point meaning offset=0 at the first trade(from the latest) offset=1 is the second trade
    transactions = req.get(
        f"https://public-api.solscan.io/account/splTransfers?account={wallet_address}&limit=10&offset={10*count}"
    ).json()

    transaction_list = []
    # While there are still transactions in data we want to add them to 'transaction_list'
    while len(transactions["data"]) != 0:
        for transaction in transactions["data"]:
            # TODO we are refferencing the symbol by it's upper-case letters so it might need fixing as it isn't always accurate
            symbol = transaction["symbol"]
            symbol = "".join(x for x in symbol if not x.islower())
            # Here we want to refer to the upper-case symbol because the lower-case letters are usually irrelevant for example wSCRT has the same value as SCRT(almost)

            if transaction["changeType"] == "inc":
                destination = "BUY"
            else:
                destination = "SELL"

            # Getting the Token's price
            wallet = Wallets("solana")
            price = wallet.get_price(
                transaction["tokenAddress"],
                transaction["blockTime"],
                symbol,
                "",
            )
            transaction_list.append(
                [
                    destination,
                    transaction["symbol"],
                    float(
                        Decimal(transaction["changeAmount"])
                        / 10 ** Decimal(transaction["decimals"])
                        * Decimal(price)
                    ),
                    float(
                        Decimal(transaction["changeAmount"])
                        / 10 ** Decimal(transaction["decimals"])
                    ),
                    price,
                    float(
                        Decimal(transaction["fee"])
                        / 10 ** Decimal(transaction["decimals"])
                    ),
                    tm.asctime(tm.localtime(int(transaction["blockTime"]))),
                ]
            )
            if uni_test and len(transaction_list) != 0:
                return transaction_list[0]

        count += 1
        transactions = req.get(
            f"https://public-api.solscan.io/account/splTransfers?account={wallet_address}&limit=10&offset={10*count}"
        ).json()
    return transaction_list[::-1]


def sol_transfers(wallet_address, uni_test):
    count = 0
    # At first we want to get the first 10 SOL transfers where wallet_address is the refferenced address and offset is our starting point meaning offset=0 at the first trade(from the latest) offset=1 is the second trade
    transactions = req.get(
        f"https://public-api.solscan.io/account/solTransfers?account={wallet_address}&limit=10&offset={10*count}"
    ).json()
    transaction_list = []
    while len(transactions["data"]) != 0:
        for transaction in transactions["data"]:

            # If the token's transfer destination is the refferenced address it means that it adds to it's token amount meaning BUY
            if transaction["dst"] == wallet_address:
                destination = "BUY"
            else:
                destination = "SELL"
            wallet = Wallets("solana")
            price = wallet.get_price_gecko("solana", "SOL", transaction["blockTime"])
            transaction_list.append(
                [
                    destination,
                    "SOL",
                    float(
                        Decimal(transaction["lamport"])
                        / 10 ** Decimal(transaction["decimals"])
                        * Decimal(price)
                    ),
                    float(
                        Decimal(transaction["lamport"])
                        / 10 ** Decimal(transaction["decimals"])
                    ),
                    price,
                    float(
                        Decimal(transaction["fee"])
                        / 10 ** Decimal(transaction["decimals"])
                    ),
                    tm.asctime(tm.localtime(int(transaction["blockTime"]))),
                ]
            )
            if uni_test and len(transaction_list) != 0:
                return transaction_list[0]
        count += 1
        transactions = req.get(
            f"https://public-api.solscan.io/account/solTransfers?account={wallet_address}&limit=10&offset={10*count}"
        ).json()
    return transaction_list[::-1]


def list_to_csv(transaction_list):
    with open(f"/home/idan/Desktop/solana_sol_transactions.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(RUNNING_SELL_HEADER)
        for trade in transaction_list:
            writer.writerow(trade)


if __name__ == "__main__":
    list_to_csv(sol_transfers("FRnCC8dBCcRabRv8xNbR5WHiGPGxdphjiRhE2qJZvwpm", False))
