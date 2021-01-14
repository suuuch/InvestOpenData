from opendatatools import fund
import unittest


class TestFutures(unittest.TestCase):
    def test_get_fund(self):
        # 获取基金公司列表
        df_total, _ = fund.get_fund_company()
        print(df_total)
        assert (len(df_total) > 0)

    def test_get_fundlist_by_company(self):
        # 根据基金公司获取基金列表
        df_total, _ = fund.get_fundlist_by_company('80000222')
        print(df_total)
        assert (len(df_total) > 0)

    def test_get_fund_type(self):
        # 根据类型获取基金信息
        df_total, _ = fund.get_fundlist_by_type('股票型基金')
        print(df_total)
        assert (len(df_total) > 0)

    def test_get_fund_nav(self):
        # 根据基金代码，获取基金历史净值
        df_total, _ = fund.get_fund_nav('000011')
        print(df_total)
        assert (len(df_total) > 0)
