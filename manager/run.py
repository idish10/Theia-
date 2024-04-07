import os
import docker
from datetime import datetime
import pattrn_robust_tracking.manager.db.mongo_for_theia as prtm
from pattrn_robust_tracking.utils.util import docker_report_to_coralogix


class PTManagerDockerHandler(object):
    def __init__(self):
        self.client = docker.from_env()
        self.client.login(
            username="pattrncapital",
            password="27wdfwf49eud588dwj",
        )

    def pull_and_run(self, image_name, env):
        try:
            self.client.api.pull(image_name)
            self.client.containers.run(
                image_name,
                environment=env,
                volumes=["/var/run/docker.sock:/var/run/docker.sock"],
            )
        except Exception as e:
            docker_report_to_coralogix(image_name, e)
            print("There was an error in docker: {0} | {1}".format(image_name, e))

    def remove_all_images(self):
        for image in self.client.images.list():
            self.client.images.remove(image=image.id, force=True)

    def remove_unused_containers(self):
        self.client.containers.prune()


def log_clients_balance(db_con_str):
    docker_handler = PTManagerDockerHandler()
    mdb_client = prtm.MongoParser(db_con_str)
    bitfinex = {"key": "", "secret": ""}
    eth: str = ""
    binance = {"key": "", "secret": ""}
    cursor = mdb_client.get_loggers_type()
    for user in cursor:
        eth = user["clients"]["wallet"]["eth"]
        bitfinex["key"] = user["clients"]["exchange"]["bitfinex_key"]
        bitfinex["secret"] = user["clients"]["exchange"]["bitfinex_secret"]
        binance["key"] = user["clients"]["exchange"]["binance_key"]
        binance["secret"] = user["clients"]["exchange"]["binance_secret"]

    # Set the timestamp of the run in Influx format
    # All records will be inserted with the same timestamp
    ts = datetime.utcnow()
    ts = str(ts.isoformat("T") + "Z")
    client = "ziv"

    docker_handler.pull_and_run(
        "pattrncapital/portfolio-logger-binance",
        [
            f"KEY={binance['key']}",
            f"SECRET={binance['secret']}",
            f"CLIENT={client}",
            f"MONGO_CONN={db_con_str}",
            f"TIMESTAMP={ts}",
        ],
    )
    docker_handler.pull_and_run(
        "pattrncapital/portfolio-logger-cex",
        [
            f"KEY={bitfinex['key']}",
            f"SECRET={bitfinex['secret']}",
            f"CLIENT={client}",
            f"MONGO_CONN={db_con_str}",
            f"TIMESTAMP={ts}",
        ],
    )

    docker_handler.pull_and_run(
        "pattrncapital/portfolio-logger-eth",
        [
            f"ADDRESS={eth}",
            f"CLIENT={client}",
            f"MONGO_CONN={db_con_str}",
            f"TIMESTAMP={ts}",
        ],
    )

    docker_handler.pull_and_run(
        "pattrncapital/portfolio-logger-writer", [f"TIMESTAMP={ts}"]
    )


def main():
    # log_clients_balance(
    #     "mongodb+srv://pattrn:pattrn1234@cluster0.ydhsz.mongodb.net/PortfolioTracking?retryWrites=true&w=majority"
    # )
    log_clients_balance(os.environ["MONGO_CONN_STR"])


if __name__ == "__main__":
    main()
