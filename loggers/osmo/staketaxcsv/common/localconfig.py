from pattrn_robust_tracking.loggers.osmo.staketaxcsv.common import ExporterTypes as et


class config:
    ibc_addresses = {}
    job = None
    debug = False
    cache = False
    limit = 20000  # max txs
    koinlynullmap = None
