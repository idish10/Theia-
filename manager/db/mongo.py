import pymongo
import datetime as dt
from bson.objectid import ObjectId


class PortfolioTrackingMongoParser(object):
    def __init__(self, connection_str):
        self.mongo_client = pymongo.MongoClient(connection_str)
        self.portfolio_tracking_db = self.mongo_client["PortfolioTracking"]
        self.portfolio_tracking_loggers_type = self.portfolio_tracking_db["loggers_type"]
        self.portfolio_tracking_clients = self.portfolio_tracking_db["clients"]
        self.portfolio_tracking_reporting = self.portfolio_tracking_db["reporting"]
        self.portfolio_tracking_token_reporting = self.portfolio_tracking_db["token_reporting"]

    def get_loggers_type(self):
        document = self.portfolio_tracking_loggers_type.find({})
        return document

    def get_clients(self):
        document = self.portfolio_tracking_clients.find({})
        return document

    def get_recent_logging(self):
        document = self.portfolio_tracking_reporting.find({})
        return document

    def get_recent_token_logging(self):
        document = self.portfolio_tracking_token_reporting.find({})
        return document

    def get_recent_token_logging_per_client(self, client_name):
        document = self.portfolio_tracking_reporting.find(
            {"client": client_name})
        return document

    def get_recent_wallet_logging_per_client(self, client_name, wallet_type):
        document = self.portfolio_tracking_token_reporting.find(
            {"client": client_name, "wallet_type": wallet_type})
        return document

    def update_log(self, client_name, field_name, balance, wallet_type="", token=""):
        # client_name, field_name, balance
        key = {"id": client_name + field_name}
        nonce = dt.datetime.today().replace(microsecond=0)
        values = {"$set": {"client": client_name, "field": field_name,
                           "balance": balance, "nonce": nonce, "wallet_type": wallet_type, "token": token}}
        self.portfolio_tracking_reporting.update_one(key, values, upsert=True)

    def update_token_log(self, client_name, field_name, balance, wallet_type="", token=""):
        # client_name, field_name, balance
        key = {"id": client_name + field_name}
        nonce = dt.datetime.today().replace(microsecond=0)
        values = {"$set": {"client": client_name, "field": field_name,
                           "balance": balance, "nonce": nonce, "wallet_type": wallet_type, "token": token}}
        self.portfolio_tracking_token_reporting.update_one(
            key, values, upsert=True)

    def get_client_tokens_per_wallet(self, client_name, wallet_type, token_collection=False):
        collection = self.portfolio_tracking_token_reporting if token_collection else self.portfolio_tracking_reporting
        cursor = collection.find(
            {"wallet_type": wallet_type, "client": client_name})
        return cursor

    def delete_sold_tokens(self, id_list, token_collection=False):
        collection = self.portfolio_tracking_token_reporting if token_collection else self.portfolio_tracking_reporting
        for id in id_list:
            collection.delete_one({'_id': ObjectId(id)})
