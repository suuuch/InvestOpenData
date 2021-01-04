# encoding: utf-8
from opendatatools import stock
import unittest


class TestStock(unittest.TestCase):
    def test_get_index_list(self):
        index_list = stock.get_index_list('SH')
        assert (len(index_list) > 0)

        index_list = stock.get_index_list('SZ')
        assert (len(index_list) > 0)

    def test_get_index_component(self):
        stock_list = stock.get_index_component('000001.SH')
        assert (len(stock_list) > 0)

        stock_list = stock.get_index_component('399001.SZ')
        assert (len(stock_list) > 0)

    def test_get_rzrq_info(self):
        df_total, df_detail = stock.get_rzrq_info(market='SH', date='2020-12-24')
        assert (len(df_total) == 1)
        assert (len(df_detail) > 100)

        df_total, df_detail = stock.get_rzrq_info(market='SZ', date='2020-12-24')
        assert (len(df_total) == 1)
        assert (len(df_detail) > 100)

    def test_get_market_money_flow(self):
        df_total, _ = stock.get_hist_money_flow_market()
        assert (len(df_total) > 0)

    def test_get_trade_detail(self):
        df_total, _ = stock.get_trade_detail(symbol='000001.SZ', trade_date='2020-12-24')
        assert (len(df_total) > 0)

    def test_get_kline(self):
        df_total, _ = stock.get_kline(symbol='000001.SZ', start_date='2020-12-01', end_date='2021-01-04', period='day')
        print(df_total)
        assert (len(df_total) > 0)
