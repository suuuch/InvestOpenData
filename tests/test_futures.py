# encoding: utf-8
from opendatatools import futures
import unittest


class TestFutures(unittest.TestCase):
    def test_get_trade_rank(self):
        markets = ['SHF', 'CZC', 'DCE', 'CFE']
        for market in markets:
            print(market)
            df, msg = futures.get_trade_rank(market)
            assert (len(df) >= 100)

    def test_get_trade_quote(self):
        df_total, _ = futures.get_quote('RB2109,SC2109')
        print(df_total)
        assert (len(df_total) > 0)

    def test_get_trade_kline(self):
        df_total, _ = futures.get_kline('1d', 'RB1809')
        print(df_total)
        assert (len(df_total) > 0)
