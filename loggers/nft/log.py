import os
import logging
from coralogix.handlers import CoralogixLogger
import opensea as ops
from pycoingecko import CoinGeckoAPI
import pattrn_robust_tracking.manager.db.mongo as prtm
from pattrn_robust_tracking.utils.util import coralogix_decorator
from pattrn_robust_tracking.loggers.wallet_logger import WalletLogger


def log_balance(address, client, mongo_conn):

    api = ops.OpenseaAPI()
    cg = CoinGeckoAPI()

    def get_my_floor_price(col_name):
        return api.collection(collection_slug=col_name)["collection"]["stats"][
            "floor_price"
        ]

    all_nft_assets = api.collections(asset_owner=address)
    s = 0
    for e in all_nft_assets:
        s += get_my_floor_price(e["slug"]) * e["owned_asset_count"]

    eth_price = cg.get_price(ids="ethereum", vs_currencies="usd")[
        "ethereum"]["usd"]
    nft_balance = s * eth_price

    print(f"NFT balance: {nft_balance}")
    field_name = f"{client}_nft_balance"
    var = WalletLogger(address, client, mongo_conn)
    var.write(client, field_name, nft_balance)
    # mdb_client = prtm.PortfolioTrackingMongoParser(mongo_conn)
    # mdb_client.update_log(client, field_name, nft_balance)
    return nft_balance


@coralogix_decorator(client=os.environ["CLIENT"], wallet_type="nft")
def test():
    balance = log_balance(
        os.environ["ADDRESS"], os.environ["CLIENT"], os.environ["MONGO_CONN"]
    )
    return balance


def main():
    test()


if __name__ == "__main__":
    main()
