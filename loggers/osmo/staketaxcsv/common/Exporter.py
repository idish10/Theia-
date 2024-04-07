import csv
import io
import logging
import time
from datetime import datetime

import pandas as pd
import pytz
from pytz import timezone
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.common import ExporterTypes as et
from pattrn_robust_tracking.loggers.osmo.staketaxcsv.settings_csv import TICKER_ALGO, TICKER_ATOM, TICKER_LUNA1, TICKER_LUNA2
from tabulate import tabulate


class Row:

    def __init__(self, timestamp, tx_type, received_amount, received_currency, sent_amount, sent_currency, fee,
                 fee_currency, exchange, wallet_address, txid, url="", z_index=0, comment=""):
        self.timestamp = timestamp
        self.tx_type = tx_type
        self.received_amount = self._format_amount(received_amount)
        self.received_currency = self._format_currency(received_currency)
        self.sent_amount = self._format_amount(sent_amount)
        self.sent_currency = self._format_currency(sent_currency)
        self.fee = self._format_amount(fee)
        self.fee_currency = fee_currency
        self.exchange = exchange
        self.wallet_address = wallet_address
        self.txid = txid
        self.url = url
        self.z_index = z_index  # Determines ordering for rows with same txid
        self.comment = comment

    def _format_currency(self, currency):
        if currency == "BLUNA":
            return "bLUNA"
        return currency

    def _format_amount(self, amount):
        """ Avoid scientific notation """
        if amount is None or amount == "":
            return ""
        elif float(amount) == 0:
            return 0
        elif float(amount) < .001:
            return "{:.9f}".format(float(amount))
        else:
            return amount

    def as_array(self):
        return [
            self.timestamp,
            self.tx_type,
            self.received_amount,
            self.received_currency,
            self.sent_amount,
            self.sent_currency,
            self.fee,
            self.fee_currency,
            self.comment,
            self.txid,
            self.url,
            self.exchange,
            self.wallet_address,
        ]

    def as_array_short(self):
        return [
            self.timestamp,
            self.tx_type,
            self.received_amount,
            self.received_currency,
            self.sent_amount,
            self.sent_currency,
            self.fee,
            self.fee_currency,
            self.txid
        ]


class Exporter:

    def __init__(self, wallet_address, localconfig=None, ticker=""):
        self.wallet_address = wallet_address
        self.rows = []
        self.is_reverse = None  # last sorted direction
        self.ticker = ticker
        if localconfig and hasattr(localconfig, "lp_treatment") and localconfig.lp_treatment:
            self.lp_treatment = localconfig.lp_treatment
        else:
            self.lp_treatment = et.LP_TREATMENT_DEFAULT

    def ingest_row(self, row):
        self.rows.append(row)

    def ingest_csv(self, default_csv):
        """ Loads default csv file into self.rows """
        with open(default_csv, 'r') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                cur_row = Row(
                    timestamp=row["timestamp"],
                    tx_type=row["tx_type"],
                    received_amount=row["received_amount"],
                    received_currency=row["received_currency"],
                    sent_amount=row["sent_amount"],
                    sent_currency=row["sent_currency"],
                    fee=row["fee"],
                    fee_currency=row["fee_currency"],
                    exchange=row["exchange"],
                    wallet_address=row["wallet_address"],
                    txid=row["txid"],
                    url=row["url"],
                    z_index=-i,
                    comment=row["comment"],
                )
                self.ingest_row(cur_row)

    def sort_rows(self, reverse=True):
        if self.is_reverse != reverse:
            self.rows.sort(
                key=lambda row: (row.timestamp, row.z_index, row.tx_type, row.sent_currency, row.received_currency),
                reverse=reverse)
            self.is_reverse = reverse

    def _rows_export(self, format, reverse=True):
        self.sort_rows(reverse)
        rows = filter(lambda row: row.tx_type in et.TX_TYPES_CSVEXPORT, self.rows)

        if format in [et.FORMAT_KOINLY, et.FORMAT_COINPANDA, et.FORMAT_COINTELLI]:
            return rows

        # For non-koinly CSVs, convert LP_DEPOSIT/LP_WITHDRAW into transfers/omit/trades
        # (due to lack of native csv import support)
        out = []
        for row in rows:
            if row.tx_type == et.TX_TYPE_LP_DEPOSIT:
                if self.lp_treatment == et.LP_TREATMENT_OMIT:
                    continue
                elif self.lp_treatment == et.LP_TREATMENT_TRANSFERS:
                    out.append(self._row_as_transfer_out(row))
                elif self.lp_treatment == et.LP_TREATMENT_TRADES:
                    out.append(self._row_as_trade(row))
                else:
                    raise Exception("Bad condition in _rows_export().  lp_treatment=%s".format(self.lp_treatment))
            elif row.tx_type == et.TX_TYPE_LP_WITHDRAW:
                if self.lp_treatment == et.LP_TREATMENT_OMIT:
                    continue
                elif self.lp_treatment == et.LP_TREATMENT_TRANSFERS:
                    out.append(self._row_as_transfer_in(row))
                elif self.lp_treatment == et.LP_TREATMENT_TRADES:
                    out.append(self._row_as_trade(row))
                else:
                    raise Exception("Bad condition in _rows_export().  lp_treatment=%s".format(self.lp_treatment))
            else:
                out.append(row)

        return out

    def _row_as_transfer_out(self, row):
        return Row(
            timestamp=row.timestamp,
            tx_type=et.TX_TYPE_TRANSFER,
            received_amount="",
            received_currency="",
            sent_amount=row.sent_amount,
            sent_currency=row.sent_currency,
            fee=row.fee,
            fee_currency=row.fee_currency,
            exchange=row.exchange,
            wallet_address=row.wallet_address,
            txid=row.txid,
            url=row.url,
            z_index=row.z_index,
            comment=row.comment,
        )

    def _row_as_transfer_in(self, row):
        return Row(
            timestamp=row.timestamp,
            tx_type=et.TX_TYPE_TRANSFER,
            received_amount=row.received_amount,
            received_currency=row.received_currency,
            sent_amount="",
            sent_currency="",
            fee=row.fee,
            fee_currency=row.fee_currency,
            exchange=row.exchange,
            wallet_address=row.wallet_address,
            txid=row.txid,
            url=row.url,
            z_index=row.z_index,
            comment=row.comment,
        )

    def _row_as_trade(self, row):
        return Row(
            timestamp=row.timestamp,
            tx_type=et.TX_TYPE_TRADE,
            received_amount=row.received_amount,
            received_currency=row.received_currency,
            sent_amount=row.sent_amount,
            sent_currency=row.sent_currency,
            fee=row.fee,
            fee_currency=row.fee_currency,
            exchange=row.exchange,
            wallet_address=row.wallet_address,
            txid=row.txid,
            url=row.url,
            z_index=row.z_index,
            comment=row.comment,
        )

    def export_print(self):
        """ Prints transactions """
        print("Transactions:")
        print(self.export_string())

    def export_string(self):
        table = [et.ROW_FIELDS]
        table.extend([row.as_array() for row in self.rows])
        return tabulate(table)

    def export_for_test(self):
        table = [et.TEST_ROW_FIELDS]
        table.extend([row.as_array_short() for row in self.rows])

        return tabulate(table)

    def export_default_csv(self, csvpath=None, truncate=0):
        self.sort_rows(reverse=True)

        rows = self.rows
        table = [et.ROW_FIELDS]
        if truncate:
            table.extend([row.as_array() for row in rows[0:truncate]])
        else:
            table.extend([row.as_array() for row in rows])

        if csvpath:
            with open(csvpath, 'w', newline='', encoding='utf-8') as f:
                mywriter = csv.writer(f)
                mywriter.writerows(table)
                logging.info("Wrote to %s", csvpath)
            return None
        else:
            # Return as string
            output = io.StringIO()
            writer = csv.writer(output, lineterminator="\n")
            writer.writerows(table)
            return output.getvalue()