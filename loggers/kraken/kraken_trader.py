import urllib.parse
import hashlib
import hmac
import base64
import time
import requests
from pattrn_robust_tracking.loggers.exchange import Exchange


api_url = "https://api.kraken.com"
api_key = "D0duZm36ExxDsfFGWK4IIEX3c7vcM72lyOWa5o3WoXB/pWneXa8QTTTA"
api_sec = "L20Q5b4r8/l7K6yBQCSvnaX3h1fqkl+LHCy+gTkp5Pwl0U0O11NpvNQ1p3duk4HzGiLY07ZYpr11joI5lILtBg=="


class KrakenSpotTrader(Exchange):
    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)

    def _filter_my_ledger_table(self, ledgers):
        """
        parsing the ledgers table and creating new withdrawls,deposits and staked_assets table's


        Args:
            ledgers (_type_): _description_

        Returns:
            _type_: _description_
        """
        withdrawls = []
        deposits = []
        staked_assets = []
        for leg in ledgers:
            if leg["type"] == "transfer":
                if leg["subtype"] == "stakingfromspot":
                    staked_assets.append(leg)
            if leg["type"] == "withdrawl":
                withdrawls.append(leg)
            if leg["type"] == "deposit":
                deposits.append(leg)
            else:
                continue
            return staked_assets, deposits, withdrawls

    def _get_kraken_signature(self, urlpath, data, secret):

        postdata = urllib.parse.urlencode(data)
        encoded = (str(data["nonce"]) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    # Attaches auth headers and returns results of a POST request
    def _kraken_request(self, uri_path, data, api_key, api_sec):
        headers = {}
        headers["API-Key"] = api_key
        # get_kraken_signature() as defined in the 'Authentication' section
        headers["API-Sign"] = self._get_kraken_signature(uri_path, data, api_sec)
        req = requests.post((api_url + uri_path), headers=headers, data=data)
        return req

    def get_ledgers(self):
        """getting ledgers
        this func assuming there is no ledgers before 1610124514(8.1.20201)


        Returns:
            _type_: _description_
        """
        ledgers = []
        start = 1610124514
        rate_limit = True
        while True:
            while rate_limit:
                resp = self._kraken_request(
                    "/0/private/Ledgers",
                    {"nonce": str(int(1000 * time.time())), "start": start},
                    api_key,
                    api_sec,
                )
                err = resp.json()["error"]
                if len(err) != 0:
                    if err[0] == "EAPI:Rate limit exceeded":
                        time.sleep(20)
                else:
                    rate_limit = False

            check = resp.json()
            temp = list(check["result"]["ledger"].values())

            if len(temp) == 0:
                break
            for move in temp:
                if move["type"] != "trade":
                    ledgers.append(move)

            start = int(temp[-1]["time"]) + 1
            rate_limit = True

        return self._filter_my_ledger_table(ledgers)

    def get_trades(self):
        """
        Retrieve information about trades/fills. 50 results are returned at a time, the most recent by default.


        Args:
            ofs : Result offset for pagination
            trades : boolean type, Default: false Whether or not to include trades related to position in output
        Returns:
            _type_: _description_
        """
        trades_list = []
        ofs = 1
        rate_limit = True
        while True:
            while rate_limit:
                resp = self._kraken_request(
                    "/0/private/TradesHistory",
                    {"nonce": str(int(1000 * time.time())), "trades": True, "ofs": ofs},
                    api_key,
                    api_sec,
                )
                err = resp.json()["error"]
                if len(err) != 0:
                    if err[0] == "EAPI:Rate limit exceeded":
                        time.sleep(20)
                else:
                    rate_limit = False

            check = resp.json()
            temp = list(check["result"]["trades"].values())

            if len(temp) == 0:
                break
            for move in temp:
                if move["type"] != "trade":
                    trades_list.append(move)

            ofs += 1
            rate_limit = True

        return trades_list


if __name__ == "__main__":
    trader = KrakenSpotTrader(key=api_key, secret=api_sec)
    staked_assets, deposits, withdrawls = trader.get_ledgers()
    trades = trader.get_trades()
