from pattrn_robust_tracking.manager.db.mongo import PortfolioTrackingMongoParser
from pattrn_robust_tracking.utils import influx


def log_all_clients_overall_portfolio(mdb_client: PortfolioTrackingMongoParser):

    all_clients_cursor = mdb_client.get_clients()
    for client in all_clients_cursor:
        client_name = client["name"]
        cursor = mdb_client.get_recent_token_logging_per_client(client_name)
        total_balance = 0
        for x in cursor:
            total_balance += x['balance']
        field = f"{client_name}_total_portfolio"

        influx.write(client_name, field, total_balance)


def log_total_aum(mdb_client: PortfolioTrackingMongoParser):
    cursor = mdb_client.get_recent_logging()
    total_balance = 0
    host = "aum"
    field = "total_aum"
    for x in cursor:
        total_balance += x['balance']

    influx.write(host, field, total_balance)


def log_client_and_wallet(mdb_client: PortfolioTrackingMongoParser):
    # all_clients_cursor = mdb_client.get_clients()
    # TODO: Switch to all clients
    for client in ["ziv"]:
        client_name = client
        cursor = mdb_client.get_recent_wallet_logging_per_client(
            client_name, "ETH")
        total_balance = 0
        for x in cursor:
            total_balance += x['balance']
        field = f"{client_name}_total_ETH_portfolio"

        influx.write(client_name, field, total_balance)
