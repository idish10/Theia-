from pattrn_robust_tracking.utils.wallets import Wallets
import dateparser


def get_account_transactions(address):
    # Specific Blockchain's api
    wallet = Wallets("tezos")

    # List of transactions to be used in the csv files
    transaction_list = []

    # If there are any ERC20 transactions then the value = True else False
    erc20_trans = True

    # Gets the ERC20 transactions
    transactions_erc20 = None
    count = 1
    # Checking whether or not there are any erc20 transactions in the specified address
    try:
        transactions_erc20 = wallet.get_transaction_page(
            count, offset=10, address=address
        )
    except:
        print("No erc20 token transactions in your wallet")
        erc20_trans = False
    while erc20_trans and transactions_erc20 is not None:
        # Continuing with the trades to the next page of transactions
        count += 1
        for t in transactions_erc20:
            timestamp = t["time"]
            fee = t["fee"]
            value = t["volume"]
            if t["sender"] == address:
                destination = "SELL"
            else:
                destination = "BUY"
            price = wallet.get_price_gecko(
                int(dateparser.parse(timestamp).timestamp()), "XTZ", "XTZ"
            )
            transaction_list.append(
                [
                    destination,
                    t["time"],
                    float(value) * float(price),
                    float(value),
                    float(price),
                    float(fee) * float(price),
                    fee,
                ]
            )
            try:
                transactions_erc20 = wallet.get_transaction_page(
                    page=count, offset=10, sort="des", erc20=True, address=address
                )
            except:
                print("No more transactions found")
                break
    return transaction_list
