from pattrn_robust_tracking.loggers.binance.binance_future_usd import BinanceFuturesUsd


class BinanceFutures:
    def __init__(self, key: str, secret: str):
        # TODO implement BinanceFutureCoin
        self.usd_user = BinanceFuturesUsd(key=key, secret=secret)
