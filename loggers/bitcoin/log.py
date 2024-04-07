import requests as req
from decimal import Decimal
import time as tm
from pattrn_robust_tracking.utils.wallets import Wallets

"""
{
    'block_height': 756846, 
    'block_hash': '00000000000000000004f4b9047c20c9193ba6a6ce625b048c267df05af6c748', 
    'block_time': 1664787728, 
    'created_at': 0, 
    'confirmations': 2, 
    'fee': 1420, 
    'hash': 'e6e8386f2eff9e97e9200dd253b2b7d05e175361c69a14f965182505c603b826', 
    'inputs_count': 1, 
    'inputs_value': 1011603128, 
    'is_coinbase': False, 
    'is_double_spend': False, 
    'is_sw_tx': True, 
    'lock_time': 756845, 
    'outputs_count': 2, 
    'outputs_value': 1011601708, 
    'sigops': 1, 
    'size': 224, 
    'version': 1, 
    'vsize': 142, 
    'weight': 566, 
    'witness_hash': 'e90af054d99f6097cae00aba71e3b67b96a1fc7a94ad4e883725f011ad8ee83a', 
    'inputs': 
    [
        {
            'prev_addresses': 
            [
                'bc1qgnerwnztlz7ne4seq0rdencmavl8xnm9ruuacf'
            ], 
            'prev_position': 0, 
            'prev_tx_hash': '94e8777c4719d150a6f8801dee5240fe06329ee676e276ed0b874668cd136b04', 
            'prev_type': 'P2WPKH_V0', 
            'prev_value': 1011603128, 
            'sequence': 4294967293
        }
    ], 
    'outputs': 
    [
        {
            'addresses': ['bc1qngh6x2r72mp4nh88l083au728z7me0plytwfj7'], 
            'value': 1007691464, 
            'type': 'P2WPKH_V0', 
            'spent_by_tx': '', 
            'spent_by_tx_position': -1
        }, 
        {
            'addresses': ['36ZxdJ4mVsLv9mQFKaNK6pwvjPLNunS7Kr'], 
            'value': 3910244, 
            'type': 'P2SH', 
            'spent_by_tx': '', 
            'spent_by_tx_position': -1
        }
    ], 
    'balance_diff': -1011603128
}
"""


def bitcoin_transfers(wallet_address):
    transaction_list = []
    count = 1
    url = f"https://chain.api.btc.com/v3/address/{wallet_address}/tx?page={count}&pagesize=10"

    transactions = req.get(url).json()["data"]["list"]
    while transactions != None:
        for transaction in transactions:
            destination = "BUY"
            if Decimal(transaction["balance_diff"]) < 0:
                destination = "SELL"
            wallet = Wallets("bitcoin")
            price = wallet.get_price_gecko("Bitcoin", "BTC", transaction["block_time"])
            transaction_list.append(
                [
                    destination,
                    "BTC",
                    Decimal(transaction["balance_diff"]) / 10**8 * Decimal(price),
                    Decimal(transaction["balance_diff"]) / 10**8,
                    price,
                    Decimal(transaction["fee"]) / 10**8 * Decimal(price),
                    tm.asctime(tm.localtime(int(transaction["block_time"]))),
                ]
            )
        count += 1
        transactions = req.get(
            f"https://chain.api.btc.com/v3/address/{wallet_address}/tx?page={count}&pagesize=10"
        ).json()["data"]["list"]
    return transaction_list[::-1]


if __name__ == "__main__":
    address = "bc1qfzccewnewgqya4k0mjpfkuxe3yc3hp3y3xyqwm"
    print(bitcoin_transfers(address))
