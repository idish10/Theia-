import os
import pattrn_robust_tracking.manager.db.mongo_for_theia as prtm
import datetime as dt
from pattrn_robust_tracking.utils import influx, webhooks
import time

# ORG = "contact@pattrn.net"
# TOKEN = "p0NIPibJckIvZhm68ROcZ7WmbH-gO6wHUq-HB18adkbatl-IKG_67UXCkwMdlcR190as_02OSLDILqyLfL7ppQ=="
# BUCKET = "Theia"
# INFLUX_URL = "https://eu-central-1-1.aws.cloud2.influxdata.com"

ORG = os.environ["INFLUXDB_ORG"]
TOKEN = os.environ["INFLUXDB_TOKEN"]
BUCKET = os.environ["INFLUXDB_BUCKET"]
INFLUX_URL = os.environ["INFLUXDB_URL"]
MEASUREMENT = "robust_portfolio_tracking"
LOGGER_MISREPORT_LIMIT = 10
TS = int(time.time() * 1000)


def write_latest_logging_to_influx(cursor):
    for x in cursor:
        suffix = ""
        host = x["client"]
        field = x["id"]
        if x["token"] != "usd":
            influx.write(host, field + "_" + "USD_VALUE", x["USD Value"], TS)
            balance = x["value"]
        else:
            suffix = "TOTAL_USD_VENUE"
            balance = x["balance"]

        influx.write(host, field + "_" + suffix, balance, TS)


def write_from_mongo(mongo_conn):
    mdb_client = prtm.MongoParser(mongo_conn)
    write_latest_logging_to_influx(mdb_client.get_logging_from_binance())
    write_latest_logging_to_influx(mdb_client.get_logging_from_bitfinex())
    write_latest_logging_to_influx(mdb_client.get_logging_from_eth())


def main():
    write_from_mongo(
        "mongodb+srv://pattrn:pattrn1234@cluster0.ydhsz.mongodb.net/PortfolioTracking?retryWrites=true&w=majority"
    )
    # write_from_mongo(os.environ["MONGO_CONN_STR"])


if __name__ == "__main__":
    main()
