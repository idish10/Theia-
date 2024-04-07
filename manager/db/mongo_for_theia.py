import pymongo
import datetime as dt
from bson.objectid import ObjectId


class MongoParser(object):
    def __init__(self, connection_str):
        self.mongo_client = pymongo.MongoClient(connection_str)
        self.portfolio_tracking_db = self.mongo_client["PattrnDB"]
        self.portfolio_tracking_loggers_type = self.portfolio_tracking_db[
            "PattrnRobustTracking"
        ]
        self.portfolio_tracking_reporting_binance = self.portfolio_tracking_db[
            "Binance"
        ]
        self.portfolio_tracking_reporting_bitfinex = self.portfolio_tracking_db[
            "Bitfinex"
        ]
        self.portfolio_tracking_reporting_eth = self.portfolio_tracking_db["Eth"]

    def get_logging_from_binance(self):
        document = self.portfolio_tracking_reporting_binance.find({})
        return document

    def get_logging_from_eth(self):
        document = self.portfolio_tracking_reporting_eth.find({})
        return document

    def get_logging_from_bitfinex(self):
        document = self.portfolio_tracking_reporting_bitfinex.find({})
        return document

    def get_loggers_type(self):
        document = self.portfolio_tracking_loggers_type.find({})
        return document

    def update_token_log(
        self,
        venue_name: str,
        client_name: str,
        token_count: int,
        token_usd_value: int,
        symb: str,
        inner_wallet_name: str = "",
    ):

        key = {
            "id": client_name + "_" + venue_name + "_" + inner_wallet_name + "_" + symb
        }
        if venue_name == "Eth":
            key = {"id": client_name + "_" + venue_name + "_" + symb}

        nonce = dt.datetime.today().replace(microsecond=0)

        if venue_name == "Binance":
            values = {
                "$set": {
                    "client": client_name,
                    "field": venue_name + "_" + inner_wallet_name,
                    "token": symb,
                    "value": token_count,
                    "USD Value": token_usd_value,
                    "nonce": nonce,
                }
            }
            self.portfolio_tracking_reporting_binance.update_one(
                key, values, upsert=True
            )

        elif venue_name == "Bitfinex":
            values = {
                "$set": {
                    "client": client_name,
                    "field": venue_name + "_" + inner_wallet_name,
                    "token": symb,
                    "value": token_count,
                    "USD Value": token_usd_value,
                    "nonce": nonce,
                }
            }
            self.portfolio_tracking_reporting_bitfinex.update_one(
                key, values, upsert=True
            )

        else:
            values = {
                "$set": {
                    "client": client_name,
                    "field": venue_name,
                    "token": symb,
                    "value": token_count,
                    "USD Value": token_usd_value,
                    "nonce": nonce,
                }
            }
            self.portfolio_tracking_reporting_eth.update_one(key, values, upsert=True)

    def update_log(
        self,
        venue_name: str,
        client_name: str,
        balance: int,
        inner_wallet_name: str = "",
    ):
        # client_name, field_name, balance
        key = {
            "id": client_name + "_" + venue_name + "_" + inner_wallet_name + "_" + "USD"
        }

        if venue_name == "Eth":
            key = {"id": client_name + "_" + venue_name + "_" + "USD"}

        nonce = dt.datetime.today().replace(microsecond=0)

        if venue_name == "Binance":
            values = {
                "$set": {
                    "client": client_name,
                    "field": venue_name + "_" + inner_wallet_name + "_" + "USD",
                    "balance": balance,
                    "nonce": nonce,
                    "token": "usd",
                }
            }
            self.portfolio_tracking_reporting_binance.update_one(
                key, values, upsert=True
            )

        elif venue_name == "Bitfinex":
            values = {
                "$set": {
                    "client": client_name,
                    "field": venue_name + "_" + inner_wallet_name + "_" + "USD",
                    "balance": balance,
                    "nonce": nonce,
                    "token": "usd",
                }
            }
            self.portfolio_tracking_reporting_bitfinex.update_one(
                key, values, upsert=True
            )

        else:
            values = {
                "$set": {
                    "client": client_name,
                    "field": venue_name + "_" + "USD",
                    "balance": balance,
                    "nonce": nonce,
                    "token": "usd",
                }
            }
            self.portfolio_tracking_reporting_eth.update_one(key, values, upsert=True)


if __name__ == "__main__":
    t = MongoParser(
        "mongodb+srv://pattrn:pattrn1234@cluster0.ydhsz.mongodb.net/PortfolioTracking?retryWrites=true&w=majority"
    )

    cursor = t.get_loggers_type()
    for c in cursor:
        print(c)
