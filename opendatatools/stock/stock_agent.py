# encoding: utf-8

from opendatatools.common import RestAgent
from opendatatools.common import date_convert, remove_non_numerical
from bs4 import BeautifulSoup
import datetime
import json, re
import pandas as pd
import io
from opendatatools.futures.futures_agent import _concat_df
import zipfile


def time_map(x):
    if x == '':
        return ''
    else:
        return datetime.datetime.strptime(x, '%Y%m%d').strftime('%Y-%m-%d')


def plan_map(x):
    if '派' not in x:
        return 0
    else:
        return '%.3f' % (float(x.split('派')[-1].split('元')[0]) / 10)


class SHExAgent(RestAgent):
    def __init__(self):
        RestAgent.__init__(self)
        headers = {
            "Accept": '*/*',
            'Referer': 'http://www.sse.com.cn/market/sseindex/indexlist/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        }
        self.add_headers(headers)

    def get_index_list(self):
        url = 'http://query.sse.com.cn/commonSoaQuery.do'
        data = {
            'sqlId': 'DB_SZZSLB_ZSLB',
        }

        response = self.do_request(url, data)
        rsp = json.loads(response)

        if 'pageHelp' in rsp:
            data = rsp['pageHelp']['data']
            return pd.DataFrame(data)
        else:
            return None

    def get_index_component(self, index):
        url = 'http://query.sse.com.cn/commonSoaQuery.do'
        data = {
            'sqlId': 'DB_SZZSLB_CFGLB',
            'indexCode': index,
        }

        response = self.do_request(url, data)
        rsp = json.loads(response)

        if 'pageHelp' in rsp:
            data = rsp['pageHelp']['data']
            return pd.DataFrame(data)
        else:
            return None

    def get_dividend(self, code):
        url = 'http://query.sse.com.cn/commonQuery.do'
        data = {
            'sqlId': 'COMMON_SSE_GP_SJTJ_FHSG_AGFH_L_NEW',
            'security_code_a': code,
        }

        response = self.do_request(url, data)
        rsp = json.loads(response)

        if 'result' in rsp:
            data = rsp['result']
            return pd.DataFrame(data)
        else:
            return None

    def get_rzrq_info(self, date):
        """
        融资融券 上交所网址
        http://www.sse.com.cn/market/othersdata/margin/sum/

        下载地址：
        http://www.sse.com.cn/market/dealingdata/overview/margin/a/rzrqjygk20201224.xls
        :param date:
        :return:
        """
        date2 = date_convert(date, '%Y-%m-%d', '%Y%m%d')
        url = 'http://www.sse.com.cn/market/dealingdata/overview/margin/a/rzrqjygk%s.xls' % date2
        response = self.do_request(url, None, method='GET', type='binary')
        if response is not None:
            excel = pd.ExcelFile(io.BytesIO(response))
            df_total = excel.parse('汇总信息').dropna()
            df_detail = excel.parse('明细信息').dropna()
            df_total['date'] = date
            df_detail['date'] = date
            return df_total, df_detail
        else:
            return None, None

    def get_pledge_info(self, date):
        date2 = date_convert(date, '%Y-%m-%d', '%Y%m%d')
        url = 'http://query.sse.com.cn/exportExcel/exportStockPledgeExcle.do?tradeDate=%s' % (date2)
        response = self.do_request(url, None, method='GET', type='binary')
        if response is not None:
            excel = pd.ExcelFile(io.BytesIO(response))
            df_total = excel.parse('交易金额汇总').dropna()
            df_detail = excel.parse('交易数量明细').dropna()
            df_total['date'] = date
            df_detail['date'] = date
            return df_total, df_detail
        else:
            return None, None


class SZExAgent(RestAgent):
    def __init__(self):
        RestAgent.__init__(self)

    def get_index_list(self):
        # url = 'http://www.szse.cn/szseWeb/ShowReport.szse'
        url = 'http://www.szse.cn/api/report/ShowReport'
        data = {
            'SHOWTYPE': 'xls',
            'CATALOGID': '1812',
        }

        response = self.do_request(url, data, method='GET', type='binary')
        df = pd.read_excel(io.BytesIO(response))
        return df

    def get_index_component(self, index):
        # url = 'http://www.szse.cn/szseWeb/ShowReport.szse'
        url = 'http://www.szse.cn/api/report/ShowReport'
        data = {
            'SHOWTYPE': 'xls',
            'CATALOGID': '1747',
            'ZSDM': index
        }

        response = self.do_request(url, data, method='GET', type='binary')
        if response is not None:
            df = pd.read_excel(io.BytesIO(response))
            return df
        else:
            return None

    def get_rzrq_info(self, date):
        """
        融资融券 深交所
        http://www.szse.cn/disclosure/margin/margin/index.html
        :param date:
        :return:
        """
        df_total = self._get_rzrq_total(date)
        df_detail = self._get_rzrq_detail(date)
        if df_total is not None:
            df_total['date'] = date
        if df_detail is not None:
            df_detail['date'] = date
        return df_total, df_detail

    def _get_rzrq_total(self, date):
        """
        http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1837_xxpl&txtDate=2020-12-24&tab2PAGENO=1&random=0.6629980185274793&TABKEY=tab2
        :param date:
        :return:
        """
        url = 'http://www.szse.cn/api/report/ShowReport'
        data = {
            'SHOWTYPE': 'xls',
            'CATALOGID': '1837_xxpl',
            'TABKEY': 'tab1',
            "txtDate": date,
        }

        response = self.do_request(url, data, method='GET', type='binary')
        if response is not None and len(response) > 0:
            df = pd.read_excel(io.BytesIO(response))
            return df
        else:
            return None

    def _get_rzrq_detail(self, date):
        # url = 'http://www.szse.cn/szseWeb/ShowReport.szse'
        url = 'http://www.szse.cn/api/report/ShowReport'
        data = {
            'SHOWTYPE': 'xls',
            'CATALOGID': '1837_xxpl',
            'TABKEY': 'tab2',
            "txtDate": date,
        }

        response = self.do_request(url, data, method='GET', type='binary')
        if response is not None and len(response) > 0:
            df = pd.read_excel(io.BytesIO(response))
            return df
        else:
            return None

    def get_pledge_info(self, date):
        df_total = self._get_pledge_info_total(date)
        df_detail = self._get_pledge_info_detail(date)
        if df_total is not None:
            df_total['date'] = date
        if df_detail is not None:
            df_detail['date'] = date
            df_detail['证券代码'] = df_detail['证券代码'].apply(lambda x: str(x).zfill(6))
        return df_total, df_detail

    def _get_pledge_info_total(self, date):
        # url = 'http://www.szse.cn/szseWeb/ShowReport.szse'
        url = 'http://www.szse.cn/api/report/ShowReport'
        data = {
            'SHOWTYPE': 'xls',
            'CATALOGID': '1837_gpzyhgxx',
            'TABKEY': 'tab1',
            "txtDate": date,
            'ENCODE': 1,
        }

        response = self.do_request(url, data, method='GET', type='binary')
        if response is not None and len(response) > 0:
            df = pd.read_excel(io.BytesIO(response))
            return df
        else:
            return None

    def _get_pledge_info_detail(self, date):
        # url = 'http://www.szse.cn/szseWeb/ShowReport.szse'
        url = 'http://www.szse.cn/api/report/ShowReport'
        data = {
            'SHOWTYPE': 'xls',
            'CATALOGID': '1837_gpzyhgxx',
            'TABKEY': 'tab2',
            "txtDate": date,
            'ENCODE': 1,
        }

        response = self.do_request(url, data, method='GET', type='binary')
        if response is not None and len(response) > 0:
            df = pd.read_excel(io.BytesIO(response))
            return df
        else:
            return None


class CSIAgent(RestAgent):
    def __init__(self):
        RestAgent.__init__(self)

    def get_index_list(self):
        url = 'http://www.csindex.com.cn/zh-CN/indices/index'

        page = 1
        result_data = []
        while True:
            data = {
                "data_type": "json",
                "page": page,
            }
            response = self.do_request(url, data, method='GET')
            rsp = json.loads(response)

            page = page + 1
            print("fetching data at page %d" % (page))
            if "list" in rsp:
                result_data.extend(rsp['list'])
                if len(rsp['list']) == 0:
                    break
            else:
                return None

        return pd.DataFrame(result_data)

    def get_index_component(self, index):
        url = 'http://www.csindex.com.cn/uploads/file/autofile/cons/%scons.xls' % (index)

        response = self.do_request(url, None, method='GET', type='binary')
        if response is not None:
            df = pd.read_excel(io.BytesIO(response))
            return df
        else:
            return None


class XueqiuAgent(RestAgent):
    def __init__(self):
        RestAgent.__init__(self)

    # 600000.SH -> SH600000
    def convert_to_xq_symbol(self, symbol):
        temp = symbol.split(".")
        return temp[1] + temp[0]

    def convert_to_xq_symbols(self, symbols):
        result = ''
        for symbol in symbols.split(','):
            result = result + self.convert_to_xq_symbol(symbol) + ','
        return result

    # SH600000 -> 600000.SH
    def convert_from_xq_symbol(self, symbol):
        market = symbol[0:2]
        code = symbol[2:]
        return code + '.' + market

    def prepare_cookies(self, url):
        response = self.do_request(url, None)
        if response is not None:
            cookies = self.get_cookies()
            return cookies
        else:
            return None

    def get_quote(self, symbols):
        url = 'https://stock.xueqiu.com/v5/stock/realtime/quotec.json'
        data = {
            'symbol': self.convert_to_xq_symbols(symbols)
        }

        # {"data":[{"symbol":"SH000001","current":3073.8321,"percent":-1.15,"chg":-35.67,"timestamp":1528427643770,"volume":6670380300,"amount":8.03515860132E10,"market_capital":1.393367880255658E13,"float_market_capital":1.254120000811718E13,"turnover_rate":0.64,"amplitude":0.91,"high":3100.6848,"low":3072.5418,"avg_price":3073.832,"trade_volume":5190400,"side":0,"is_trade":true,"level":1,"trade_session":null,"trade_type":null}],"error_code":0,"error_description":null}
        response = self.do_request(url, data, method='GET')

        if response is not None:
            jsonobj = json.loads(response)
            if jsonobj['error_code'] == 0:
                result = []
                for rsp in jsonobj['data']:
                    result.append({
                        'time': datetime.datetime.fromtimestamp(rsp['timestamp'] / 1000),
                        'symbol': self.convert_from_xq_symbol(rsp['symbol']),
                        'high': rsp['high'],
                        'low': rsp['low'],
                        'last': rsp['current'],
                        'change': rsp['chg'],
                        'percent': rsp['percent'],
                        'volume': rsp['volume'],
                        'amount': rsp['amount'],
                        'turnover_rate': rsp['turnover_rate'],
                        'market_capital': rsp['market_capital'],
                        'float_market_capital': rsp['float_market_capital'],
                        'is_trading': rsp['is_trade'],
                    })

                return pd.DataFrame(result), ''
            else:
                return None, jsonobj['error_description']
        else:
            return None, '请求数据失败'

    def get_kline(self, symbol, timestamp, period, count):
        url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json'
        data = {
            'symbol': self.convert_to_xq_symbol(symbol),
            'begin': timestamp,
            'period': period,
            'type': 'before',
            'count': count,
            'indicator': 'kline',
        }

        cookies = self.prepare_cookies('https://xueqiu.com/hq')

        response = self.do_request(url, data, cookies=cookies, method='GET')
        if response is not None:
            jsonobj = json.loads(response)
            if jsonobj['error_code'] == 0:
                result = []
                for rsp in jsonobj['data']['item']:
                    result.append({
                        'symbol': symbol,
                        'time': datetime.datetime.fromtimestamp(rsp[0] / 1000),
                        'volume': rsp[1],
                        'open': rsp[2],
                        'high': rsp[3],
                        'low': rsp[4],
                        'last': rsp[5],
                        'change': rsp[6],
                        'percent': rsp[7],
                        'turnover_rate': rsp[8],
                    })

                return pd.DataFrame(result), ''
            else:
                return None, jsonobj['error_description']
        else:
            return None, '请求数据失败'

    def get_kline_multisymbol(self, symbols, timestamp, period, count):

        cookies = self.prepare_cookies('https://xueqiu.com/hq')
        url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json'

        result = []
        for symbol in symbols:

            data = {
                'symbol': self.convert_to_xq_symbol(symbol),
                'begin': timestamp,
                'period': period,
                'type': 'before',
                'count': count,
                'indicator': 'kline',
            }

            response = self.do_request(url, data, cookies=cookies, method='GET')

            if response is not None:
                jsonobj = json.loads(response)
                if jsonobj['error_code'] == 0:
                    for rsp in jsonobj['data']['item']:
                        result.append({
                            'symbol': symbol,
                            'time': datetime.datetime.fromtimestamp(rsp[0] / 1000),
                            'volume': rsp[1],
                            'open': rsp[2],
                            'high': rsp[3],
                            'low': rsp[4],
                            'last': rsp[5],
                            'change': rsp[6],
                            'percent': rsp[7],
                            'turnover_rate': rsp[8],
                        })

        return pd.DataFrame(result), ''

    def get_kline_multitimestamp(self, symbol, timestamps, period, count):

        cookies = self.prepare_cookies('https://xueqiu.com/hq')
        url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json'

        result = []
        for timestamp in timestamps:
            data = {
                'symbol': self.convert_to_xq_symbol(symbol),
                'begin': timestamp,
                'period': period,
                'type': 'before',
                'count': count,
                'indicator': 'kline',
            }

            response = self.do_request(url, data, cookies=cookies, method='GET')

            if response is not None:
                jsonobj = json.loads(response)
                if jsonobj['error_code'] == 0:
                    for rsp in jsonobj['data']['item']:
                        result.append({
                            'symbol': symbol,
                            'time': datetime.datetime.fromtimestamp(rsp[0] / 1000),
                            'volume': rsp[1],
                            'open': rsp[2],
                            'high': rsp[3],
                            'low': rsp[4],
                            'last': rsp[5],
                            'change': rsp[6],
                            'percent': rsp[7],
                            'turnover_rate': rsp[8],
                        })

        return pd.DataFrame(result), ''


class SinaAgent(RestAgent):
    def __init__(self):
        RestAgent.__init__(self)

    @staticmethod
    def clear_text(text):
        return text.replace('\n', '').strip()

    def get_adj_factor(self, symbol):
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        if month < 4:
            quarter = 1
        elif month < 7:
            quarter = 2
        elif month < 10:
            quarter = 3
        else:
            quarter = 4

        temp = symbol.split(".")
        url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vMS_FuQuanMarketHistory/stockid/%s.phtml' % temp[0]

        curr_year = year
        curr_quarter = quarter
        result_list = []
        no_data_cnt = 0
        while True:
            print('getting data for year = %d, quarter = %d' % (curr_year, curr_quarter))
            param = {
                'year': curr_year,
                'jidu': curr_quarter,
            }
            response = self.do_request(url, param, method='GET', encoding='gb18030')
            soup = BeautifulSoup(response, "html5lib")
            divs = soup.find_all('div')

            data = []
            for div in divs:
                if div.has_attr('class') and 'tagmain' in div['class']:
                    tables = div.find_all('table')

                    for table in tables:
                        if table.has_attr('id') and table['id'] == 'FundHoldSharesTable':
                            rows = table.findAll('tr')
                            for row in rows:
                                cols = row.findAll('td')
                                if len(cols) == 8:
                                    date = SinaAgent.clear_text(cols[0].text)
                                    adjust_factor = SinaAgent.clear_text(cols[7].text)

                                    if date == '日期':
                                        continue

                                    data.append({
                                        "date": date,
                                        "adjust_factor": adjust_factor,
                                    })

            result_list.extend(data)
            if len(data) == 0:
                no_data_cnt = no_data_cnt + 1
                if no_data_cnt >= 3:
                    break

            # prepare for next round
            if curr_quarter == 1:
                curr_year = curr_year - 1
                curr_quarter = 4
            else:
                curr_quarter = curr_quarter - 1

        return pd.DataFrame(result_list), ""

    # 600000.SH -> SH600000
    def convert_to_sina_symbol(self, symbol):
        temp = symbol.split(".")
        return temp[1].lower() + temp[0]

    def get_trade_detail(self, symbol, trade_date):
        assert '服务已下线'


class CNInfoAgent(RestAgent):
    base_info_columns = {'F032V': '所属行业',
                         'MARKET': '所属市场',
                         'F010D': '成立日期',
                         'F006V': '邮政编码',
                         'F044V': '入选指数',
                         'F015V': '主营业务',
                         'F013V': '联系电话',
                         'F007N': '每股面值(元)',
                         'F003V': '法人代表',
                         'F001V': '英文名称',
                         'F011V': '官方网址',
                         'F017V': '机构简介',
                         'F005V': '办公地址',
                         'F014V': '传真',
                         'F004V': '注册地址',
                         'F012V': '电子邮箱',
                         'F006D': '上市日期',
                         'F002V': '曾用简称',
                         'ORGNAME': '公司名称',
                         'F016V': '经营范围',
                         'F018V': '公司董秘',
                         'F042V': '总经理',
                         'ASECNAME': '证券名称',
                         'ASECCODE': '证券代码',
                         'BSECNAME': 'BSECNAME',
                         'BSECCODE': 'BSECCODE',
                         'HSECNAME': 'HSECNAME',
                         'HSECCODE': 'HSECCODE',
                         'F052V': 'F052V',
                         'F053V': 'F053V',
                         'SECCODE': '交易所代码',
                         'F028N': '首发募资净额(万元)',
                         'F008N': '首发价格(元)',
                         'F047V': '首发主承销商',

                         }
    main_report_columns = {'ENDDATE': 'END_DATE',
                           'F004N': '基本每股收益(元)',
                           'F008N': '每股净资产(元)',
                           'F010N': '每股资本公积金(元)',
                           'F011N': '营业利润率(%)',
                           'F016N': '总资产报酬率(%)',
                           'F017N': '净利润率(%)',
                           'F022N': '应收账款周转率(次)',
                           'F023N': '存货周转率(次)',
                           'F025N': '总资产周转率(次)',
                           'F026N': '固定资产周转率(次)',
                           'F029N': '流动资产周转率(次)',
                           'F041N': '资产负债比率(%)',
                           'F042N': '流动比率',
                           'F043N': '速动比率',
                           'F052N': '营业收入增长率(%)',
                           'F053N': '净利润增长率(%)',
                           'F054N': '净资产增长率(%)',
                           'F056N': '总资产增长率(%)',
                           'F058N': '营业利润增长率(%)',
                           'F067N': 'F067N',
                           'F078N': 'F078N', }
    circulating_stockholders_columns = {
        'F001D': '公布时间',
        'F002V': '股东名称',
        'F003N': '持股数量(万股)',
        'F004N': '持股比例',
        'F005N': '股东名词',
        'F006V': '股份性质',
        'F007V': '持股比例变动情况(%)',
    }
    shareholder_structure_columns = {
        'F002V': '变动原因',
        'F003N': '总股本',
        'F021N': '已流通股份',
        'F022N': '人民币普通股/CDR',
        'F023N': '境内上市外资股(B股)',
        'F024N': '境外上市外资股(H股)',
        'F028N': '流通受限股份',
        'VARYDATE': '变动日期',
    }
    fund_holding_columns = {
        'ENDDATE': '报告期',
        'F001N': '基金覆盖家数(只)',
        'F002N': '持股总数(股)',
    }

    def __init__(self):
        RestAgent.__init__(self)

    def get_company_base_data(self, symbol):

        url = 'http://www.cninfo.com.cn/data20/companyOverview/getCompanyIntroduction'
        data = {
            'scode': symbol
        }

        response = self.do_request(url, param=data, method='GET', type='json')
        data = response['data']
        if data['resultCode'] != '200':
            return None, data['resultMsg']
        rst = dict()
        records = data['records'][0]
        rst.update(records['basicInformation'][0])
        rst.update(records['listingInformation'][0])
        df = pd.DataFrame([rst])
        df = df.rename(columns=self.base_info_columns)
        return df, ''

    def __get_records_data(self, url, data):
        response = self.do_request(url, param=data, method='GET', type='json')
        data = response['data']
        if data['resultCode'] != '200':
            return None, data['resultMsg']
        return data['records']

    def __get_report_data(self, url, data, periods):
        rst = list()
        records = self.__get_records_data(url, data)[0]
        rst.extend(records.get(periods))
        df = pd.DataFrame(rst)
        return df

    def get_report_main_data(self, symbol, periods='year'):
        url = 'http://www.cninfo.com.cn/data20/financialData/getMainIndicators'
        data = {
            'scode': symbol,
            'sign': '1'
        }
        df = self.__get_report_data(url, data, periods)
        df = df.rename(columns=self.main_report_columns)
        df['symbol'] = symbol
        if len(df) > 0:
            return df, ''
        else:
            assert '找不到对应数据'

    def get_report_data(self, symbol, report_type, periods='year'):
        if report_type == 'lrb':
            url = 'http://www.cninfo.com.cn/data20/financialData/getIncomeStatement'
        elif report_type == 'fzb':
            url = 'http://www.cninfo.com.cn/data20/financialData/getBalanceSheets'
        elif report_type == 'llb':
            url = 'http://www.cninfo.com.cn/data20/financialData/getCashFlowStatement'
        else:
            return None, '不支持报表类型'

        data = {
            'scode': symbol,
            'sign': 1
        }
        df = self.__get_report_data(url, data, periods)
        df = df.set_index('index')
        df = df.T
        df['symbol'] = symbol
        if len(df) > 0:
            return df, ''
        else:
            assert '找不到对应数据'

    def get_shareholder_structure(self, symbol):
        url = 'http://www.cninfo.com.cn/data20/stockholderCapital/getStockStructure'
        data = {
            'scode': symbol
        }
        records = self.__get_records_data(url, data)
        df = pd.DataFrame(records)
        df = df.rename(columns=self.shareholder_structure_columns)
        df['symbol'] = symbol
        return df, ''

    def get_dividend(self, symbol):
        pass

    def get_top_ten_circulating_stockholders(self, symbol):
        url = 'http://www.cninfo.com.cn/data20/stockholderCapital/getTopTenCirculatingStockholders'
        data = {
            'scode': symbol
        }
        records = self.__get_records_data(url, data)
        df = pd.DataFrame(records)
        df = df.rename(columns=self.circulating_stockholders_columns)
        df['symbol'] = symbol
        return df, ''

    def get_stock_fund_holding(self, symbol):
        url = 'http://www.cninfo.com.cn/data20/stockholderCapital/getFundHoldings'
        data = {
            'scode': symbol
        }
        records = self.__get_records_data(url, data)
        df = pd.DataFrame(records)
        df = df.rename(columns=self.fund_holding_columns)
        df['symbol'] = symbol
        return df, ''


class EastMoneyAgent(RestAgent):
    """
    大盘资金流向：http://data.eastmoney.com/zjlx/dpzjlx.html

    """

    def __init__(self):
        RestAgent.__init__(self)

    def _parse_hist_money_flow(self, response):
        jsonobj = json.loads(response)
        result = []
        columns_list = ['Time', 'ZLJLRJE', 'XDJLRJE', 'ZDJLRJE', 'DDJLRJE',
                        'CDDJLRJE', 'ZLJLRZB', 'XDJLRZB', 'ZDJLRZB', 'DDJLRZB',
                        'CDDJLRZB', 'SZSPJ', 'SZZDF', 'SZSPJ', 'SZZDF']
        for data in jsonobj['data']['klines']:
            items = data.split(',')
            result.append(dict(zip(columns_list, items)))
        return pd.DataFrame(result)

    def _get_hist_money_flow(self, url):
        response = self.do_request(url)
        if response is None:
            return None, '获取数据失败'

        df = self._parse_hist_money_flow(response)
        return df, ''

    def get_hist_money_flow(self, symbol):
        url = 'http://ff.eastmoney.com//EM_CapitalFlowInterface/api/js?type=hff&rtntype=2&js={"data":(x)}&check=TMLBMSPROCR&acces_token=1942f5da9b46b069953c873404aad4b5&id=%s' % symbol
        return self._get_hist_money_flow(url)

    def get_hist_money_flow_market(self):
        """
        大盘资金流向： http://data.eastmoney.com/zjlx/dpzjlx.html
        接口： http://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?lmt=0&klt=101&secid=1.000001&secid2=0.399001&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18308780832859698127_1608864632777
        :return:
        """
        url = 'http://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?lmt=0' \
              '&klt=101&secid=1.000001&secid2=0.399001&fields1=f1,f2,f3,f7' \
              '&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65' \
              '&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18308780832859698127_1608864632777'
        response = self.do_request(url)
        if response is None:
            return None, '获取数据失败'

        # get data from html
        pattern = re.compile(r'\d+\_\d+\((.*?)\)')
        json_rsp = pattern.findall(response)[0]
        df = self._parse_hist_money_flow(json_rsp)
        return df, ''

