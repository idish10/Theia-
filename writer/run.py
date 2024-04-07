import os
import pattrn_robust_tracking.manager.db.mongo as prtm
import datetime as dt
from pattrn_robust_tracking.utils import influx, webhooks
import pattrn_robust_tracking.writer.advanced_logging as adlg


# ORG = "contact@pattrn.net"
# TOKEN = "p0NIPibJckIvZhm68ROcZ7WmbH-gO6wHUq-HB18adkbatl-IKG_67UXCkwMdlcR190as_02OSLDILqyLfL7ppQ=="
# BUCKET = "Theia"
# INFLUX_URL = "https://eu-central-1-1.aws.cloud2.influxdata.com"
# MEASUREMENT = "robust_portfolio_tracking"

ORG = os.environ["INFLUXDB_ORG"]
TOKEN = os.environ["INFLUXDB_TOKEN"]
BUCKET = os.environ["INFLUXDB_BUCKET"]
INFLUX_URL = os.environ["INFLUXDB_URL"]
TS = os.environ["TIMESTAMP"]
MEASUREMENT = "robust_portfolio_tracking"
LOGGER_MISREPORT_LIMIT = 10


def write_latest_logging_to_influx(cursor):
    for x in cursor:
        host = x["client"]
        field = x["field"]
        balance = x["balance"]
        nonce = x["nonce"]

        # Report to slack if the reporting nonce hasn't changed
        if nonce < dt.datetime.now() - dt.timedelta(hours=LOGGER_MISREPORT_LIMIT):
            webhooks.post_to_slack(
                "{} nonce wasn't updated for {} hours!".format(
                    field, LOGGER_MISREPORT_LIMIT
                )
            )

        influx.write(host, field, balance)


def write_from_mongo(mongo_conn):
    mdb_client = prtm.PortfolioTrackingMongoParser(mongo_conn)
    write_latest_logging_to_influx(mdb_client.get_recent_logging())
    write_latest_logging_to_influx(mdb_client.get_recent_token_logging())
    adlg.log_total_aum(mdb_client)
    adlg.log_all_clients_overall_portfolio(mdb_client)
    adlg.log_client_and_wallet(mdb_client)


def main():
    write_from_mongo(os.environ["MONGO_CONN_STR"])


if __name__ == "__main__":
    main()
