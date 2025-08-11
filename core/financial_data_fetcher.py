#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票财务数据获取工具
支持换手率、市盈率、市值等财务指标获取
"""

import datetime
import json
import time
from typing import Dict, Optional

import requests


class FinancialDataFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

        # 东方财富财务数据字段映射
        self.field_mapping = {
            'f43': '换手率',
            'f44': '最新价',
            'f45': '最高价',
            'f46': '最低价',
            'f47': '开盘价',
            'f48': '昨收价',
            'f49': '涨跌额',
            'f50': '涨跌幅',
            'f51': '成交量',
            'f52': '成交额',
            'f55': '振幅',
            'f57': '市盈率(动态)',
            'f58': '市盈率(静态)',
            'f60': '量比',
            'f62': '委比',
            'f71': '涨速',
            'f80': '总股本',
            'f84': '流通股本',
            'f85': '总市值',
            'f86': '流通市值',
            'f92': '52周最高',
            'f104': '52周最低',
            'f105': '年内最高',
            'f107': '年内最低',
            'f110': '每股收益',
            'f111': '每股净资产',
            'f116': '总市值',
            'f117': '流通市值',
            'f127': '市净率',
            'f128': '市销率',
            'f135': 'ROE',
            'f136': 'ROA',
            'f137': '毛利率',
            'f138': '净利率',
            'f139': '资产负债率',
            'f140': '流动比率',
            'f141': '速动比率',
            'f142': '存货周转率',
            'f143': '应收账款周转率',
            'f144': '总资产周转率',
            'f145': '固定资产周转率',
            'f146': '股东权益周转率',
            'f147': '营业收入增长率',
            'f148': '净利润增长率',
            'f149': '净资产增长率',
            'f161': '委差',
            'f162': '外盘',
            'f163': '内盘',
            'f164': '换手率',
            'f167': '市净率',
            'f168': '市销率',
            'f169': '市盈率TTM',
            'f170': '市盈率LYR',
            'f173': '量比',
            'f177': '委比',
            'f183': '5日均线',
            'f184': '10日均线',
            'f185': '20日均线',
            'f186': '30日均线',
            'f187': '60日均线',
            'f188': '120日均线',
            'f189': '250日均线',
            'f190': 'MACD',
            'f191': 'KDJ',
            'f192': 'RSI',
            'f193': '布林带',
            'f194': '威廉指标',
            'f195': 'CCI',
            'f196': 'OBV',
            'f197': 'DMI',
            'f199': 'BIAS',
            'f250': '主力净流入',
            'f251': '超大单净流入',
            'f252': '大单净流入',
            'f253': '中单净流入',
            'f254': '小单净流入',
            'f255': '主力净流入占比',
            'f256': '超大单净流入占比',
            'f257': '大单净流入占比',
            'f258': '中单净流入占比',
            'f262': '主力净流入5日',
            'f263': '超大单净流入5日',
            'f264': '大单净流入5日',
            'f266': '中单净流入5日',
            'f267': '小单净流入5日',
            'f268': '主力净流入10日',
            'f269': '超大单净流入10日',
            'f270': '大单净流入10日',
            'f271': '中单净流入10日',
            'f273': '小单净流入10日',
            'f274': '主力净流入20日',
            'f275': '超大单净流入20日',
            'f280': '行业',
            'f281': '概念',
            'f282': '地域',
            'f284': '上市时间',
            'f285': '所属板块',
            'f286': '主营业务',
            'f287': '公司简介',
            'f292': '最新公告'
        }

    def get_eastmoney_financial_data(self, stock_code: str) -> Optional[Dict]:
        """
        从东方财富获取财务数据
        """
        try:
            # 构建股票ID
            if stock_code.startswith('sz'):
                secid = f"0.{stock_code[2:]}"
            elif stock_code.startswith('sh'):
                secid = f"1.{stock_code[2:]}"
            else:
                print(f"❌ 不支持的股票代码格式: {stock_code}")
                return None

            # 东方财富财务数据API
            url = "http://push2.eastmoney.com/api/qt/stock/get"

            # 构建字段参数 - 包含所有可用字段
            fields = ','.join(self.field_mapping.keys())

            params = {
                'secid': secid,
                'fields': fields,
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fltt': '2',
                'invt': '2',
                'wbp2u': '|0|0|0|web'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    stock_data = data['data']

                    # 解析所有字段
                    financial_data = {
                        '股票代码': stock_code,
                        '股票名称': stock_data.get('f58', ''),
                        '数据来源': '东方财富',
                        '数据时间戳': datetime.datetime.now().isoformat()
                    }

                    # 遍历所有字段并解析
                    for field_code, field_name in self.field_mapping.items():
                        value = stock_data.get(field_code)
                        if value is not None and value != '' and value != '-':
                            try:
                                # 根据字段类型进行格式化
                                if field_code in ['f43', 'f164']:  # 换手率
                                    financial_data[field_name] = f"{float(value):.2f}%"
                                elif field_code in ['f57', 'f58', 'f169', 'f170']:  # 市盈率
                                    financial_data[field_name] = f"{float(value):.2f}"
                                elif field_code in ['f85', 'f86', 'f116', 'f117']:  # 市值
                                    if float(value) >= 100000000:  # 大于1亿
                                        financial_data[field_name] = f"{float(value) / 100000000:.2f}亿"
                                    else:
                                        financial_data[field_name] = f"{float(value):,.0f}"
                                elif field_code in ['f51', 'f52']:  # 成交量和成交额
                                    if field_code == 'f52' and float(value) >= 100000000:  # 成交额大于1亿
                                        financial_data[field_name] = f"{float(value) / 100000000:.2f}亿"
                                    else:
                                        financial_data[field_name] = f"{float(value):,.0f}"
                                elif field_code in ['f44', 'f45', 'f46', 'f47', 'f48', 'f49']:  # 价格相关
                                    financial_data[field_name] = f"{float(value):.2f}"
                                elif field_code in ['f50', 'f55', 'f60', 'f62', 'f71']:  # 百分比相关
                                    financial_data[field_name] = f"{float(value):.2f}%"
                                else:
                                    financial_data[field_name] = value
                            except (ValueError, TypeError):
                                financial_data[field_name] = value
                        else:
                            financial_data[field_name] = '-'

                    return financial_data
            return None

        except Exception as e:
            print(f"获取东方财富财务数据失败: {e}")
            return None

    def get_sina_financial_data(self, stock_code: str) -> Optional[Dict]:
        """
        从新浪财经获取财务数据
        使用实时行情API + 财务数据API的组合方式
        """
        try:
            # 更新headers，添加Referer
            sina_headers = self.headers.copy()
            sina_headers['Referer'] = 'http://finance.sina.com.cn'

            # 1. 获取实时行情数据
            realtime_url = f"http://hq.sinajs.cn/list={stock_code}"
            realtime_response = requests.get(realtime_url, headers=sina_headers, timeout=10)

            if realtime_response.status_code != 200:
                return None

            # 解析实时行情数据
            realtime_text = realtime_response.text
            if f'v_{stock_code}=' not in realtime_text and f'hq_str_{stock_code}=' not in realtime_text:
                return None

            # 提取数据部分
            if f'hq_str_{stock_code}=' in realtime_text:
                data_part = realtime_text.split('="')[1].split('";')[0]
                realtime_data = data_part.split(',')

                if len(realtime_data) < 32:
                    return None

                # 新浪实时行情数据字段解析
                # 0:股票名称, 1:今日开盘价, 2:昨日收盘价, 3:当前价格, 4:今日最高价, 5:今日最低价
                # 6:竞买价, 7:竞卖价, 8:成交量, 9:成交额, 10:买一量, 11:买一价, 12:买二量, 13:买二价
                # 14:买三量, 15:买三价, 16:买四量, 17:买四价, 18:买五量, 19:买五价
                # 20:卖一量, 21:卖一价, 22:卖二量, 23:卖二价, 24:卖三量, 25:卖三价
                # 26:卖四量, 27:卖四价, 28:卖五量, 29:卖五价, 30:日期, 31:时间

                def safe_float(value, default=0):
                    try:
                        return float(value) if value and value != '' else default
                    except (ValueError, TypeError):
                        return default

                def safe_int(value, default=0):
                    try:
                        return int(float(value)) if value and value != '' else default
                    except (ValueError, TypeError):
                        return default

                current_price = safe_float(realtime_data[3])
                pre_close = safe_float(realtime_data[2])
                change = current_price - pre_close
                change_pct = (change / pre_close * 100) if pre_close > 0 else 0

                financial_data = {
                    '股票代码': stock_code,
                    '股票名称': realtime_data[0] if len(realtime_data) > 0 else '',
                    '当前价格': current_price,
                    '昨收价': pre_close,
                    '开盘价': safe_float(realtime_data[1]),
                    '最高价': safe_float(realtime_data[4]),
                    '最低价': safe_float(realtime_data[5]),
                    '成交量': safe_int(realtime_data[8]),
                    '成交额': safe_float(realtime_data[9]),
                    '涨跌额': change,
                    '涨跌幅': f"{change_pct:.2f}%",
                    '数据来源': '新浪财经',
                    '数据时间戳': datetime.datetime.now().isoformat()
                }

                # 2. 尝试获取财务指标数据（如果可用）
                try:
                    # 尝试使用新浪财经的财务数据API
                    finance_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
                    finance_params = {
                        'page': 1,
                        'num': 1,
                        'sort': 'symbol',
                        'asc': 1,
                        'node': 'hs_a',
                        'symbol': stock_code
                    }

                    finance_response = requests.get(finance_url, params=finance_params, headers=sina_headers, timeout=5)

                    if finance_response.status_code == 200:
                        finance_data = finance_response.json()
                        if finance_data and len(finance_data) > 0:
                            stock_info = finance_data[0]

                            # 添加财务指标
                            financial_data.update({
                                '市盈率': safe_float(stock_info.get('per', 0)),
                                '市净率': safe_float(stock_info.get('pb', 0)),
                                '总市值': safe_float(stock_info.get('mktcap', 0)),
                                '流通市值': safe_float(stock_info.get('nmc', 0)),
                                '换手率': f"{safe_float(stock_info.get('turnoverratio', 0)):.2f}%"
                            })
                except Exception as e:
                    # 如果财务数据获取失败，继续使用实时行情数据
                    print(f"新浪财经财务指标获取失败，使用实时行情数据: {e}")

                return financial_data
                
            return None

        except Exception as e:
            print(f"获取新浪财经财务数据失败: {e}")
            return None

    def get_tencent_financial_data(self, stock_code: str) -> Optional[Dict]:
        """
        从腾讯财经获取财务数据
        """
        try:
            # 腾讯财经财务数据API
            url = f"http://qt.gtimg.cn/q={stock_code}"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200 and response.text.strip():
                # 解析腾讯财经数据
                if f'v_{stock_code}=' in response.text:
                    data_part = response.text.split('="')[1].split('";')[0]
                    stock_data = data_part.split('~')

                    # 腾讯财经数据字段解析
                    # 0:股票名称, 1:股票代码, 2:当前价格, 3:昨收价, 4:开盘价, 5:成交量, 6:外盘, 7:内盘
                    # 8:买一价, 9:买一量, 10:买二价, 11:买二量, 12:买三价, 13:买三量, 14:买四价, 15:买四量, 16:买五价, 17:买五量
                    # 18:卖一价, 19:卖一量, 20:卖二价, 21:卖二量, 22:卖三价, 23:卖三量, 24:卖四价, 25:卖四量, 26:卖五价, 27:卖五量
                    # 28:最近逐笔成交, 29:时间, 30:涨跌, 31:涨跌额, 32:涨跌幅, 33:最高价, 34:最低价, 35:成交量/手, 36:成交额/万
                    # 37:换手率, 38:市盈率, 39:市净率, 40:总市值, 41:流通市值, 42:涨速, 43:5分钟涨跌, 44:60日涨跌幅, 45:年初至今涨跌幅

                    def safe_float(value, default=0):
                        try:
                            return float(value) if value and value != '' else default
                        except (ValueError, TypeError):
                            return default

                    def safe_int(value, default=0):
                        try:
                            return int(float(value)) if value and value != '' else default
                        except (ValueError, TypeError):
                            return default

                    financial_data = {
                        '股票代码': stock_code,
                        '股票名称': stock_data[0] if len(stock_data) > 0 else '',
                        '当前价格': safe_float(stock_data[2]),
                        '昨收价': safe_float(stock_data[3]),
                        '开盘价': safe_float(stock_data[4]),
                        '最高价': safe_float(stock_data[33]),
                        '最低价': safe_float(stock_data[34]),
                        '成交量': safe_int(stock_data[5]),
                        '成交额': safe_float(stock_data[36]) * 10000,  # 转换为元
                        '换手率': f"{safe_float(stock_data[37]):.2f}%" if safe_float(stock_data[37]) > 0 else '-',
                        '市盈率': safe_float(stock_data[38]),
                        '市净率': safe_float(stock_data[39]),
                        '总市值': safe_float(stock_data[40]),
                        '流通市值': safe_float(stock_data[41]),
                        '涨跌额': safe_float(stock_data[31]),
                        '涨跌幅': f"{safe_float(stock_data[32]):.2f}%" if safe_float(stock_data[32]) != 0 else '-',
                        '数据来源': '腾讯财经',
                        '数据时间戳': datetime.datetime.now().isoformat()
                    }

                    return financial_data
            return None

        except Exception as e:
            print(f"获取腾讯财经财务数据失败: {e}")
            return None

    def get_financial_data(self, stock_code: str, data_source: str = 'auto') -> Optional[Dict]:
        """
        获取财务数据
        data_source: 'auto' - 自动选择, 'eastmoney' - 东方财富, 'sina' - 新浪财经, 'tencent' - 腾讯财经
        """
        print(f"正在获取 {stock_code} 的财务数据...")

        if data_source == 'auto':
            # 自动选择数据源
            sources = [
                ('东方财富', self.get_eastmoney_financial_data),
                ('新浪财经', self.get_sina_financial_data),
                ('腾讯财经', self.get_tencent_financial_data)
            ]

            for source_name, source_func in sources:
                print(f"尝试从 {source_name} 获取数据...")
                data = source_func(stock_code)
                if data is not None:
                    print(f"✅ 成功从 {source_name} 获取到数据")
                    return data
                else:
                    print(f"❌ 从 {source_name} 获取数据失败")
                    time.sleep(1)

            print("❌ 所有数据源都无法获取数据")
            return None

        elif data_source == 'eastmoney':
            return self.get_eastmoney_financial_data(stock_code)
        elif data_source == 'sina':
            return self.get_sina_financial_data(stock_code)
        elif data_source == 'tencent':
            return self.get_tencent_financial_data(stock_code)
        else:
            print(f"❌ 不支持的数据源: {data_source}")
            return None

    def save_to_json(self, data: Dict, stock_code: str, filename: str = None):
        """保存财务数据到JSON文件"""
        if filename is None:
            filename = f"{stock_code}_financial_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 数据已保存到: {filename}")

    def print_financial_summary(self, data: Dict):
        """打印财务数据摘要"""
        if not data:
            print("❌ 没有数据可显示")
            return

        print("\n" + "=" * 80)
        print(f"📊 {data['股票代码']} 财务数据")
        print("=" * 80)

        # 基本信息
        print(f"股票名称: {data.get('股票名称', 'N/A')}")
        print(f"数据来源: {data.get('数据来源', 'N/A')}")
        print(f"更新时间: {data.get('数据时间戳', 'N/A')}")
        print()

        # 价格信息
        print("💰 价格信息:")
        print(f"  当前价格: {data.get('当前价格', 'N/A')}")
        print(f"  开盘价: {data.get('开盘价', 'N/A')}")
        print(f"  最高价: {data.get('最高价', 'N/A')}")
        print(f"  最低价: {data.get('最低价', 'N/A')}")
        print(f"  昨收价: {data.get('昨收价', 'N/A')}")
        print(f"  涨跌额: {data.get('涨跌额', 'N/A')}")
        print(f"  涨跌幅: {data.get('涨跌幅', 'N/A')}")
        print()

        # 交易信息
        print("📈 交易信息:")
        print(f"  成交量: {data.get('成交量', 'N/A')}")
        print(f"  成交额: {data.get('成交额', 'N/A')}")
        print(f"  换手率: {data.get('换手率', 'N/A')}")
        print()

        # 估值指标
        print("📊 估值指标:")
        print(f"  市盈率(动态): {data.get('市盈率(动态)', 'N/A')}")
        print(f"  市盈率(静态): {data.get('市盈率(静态)', 'N/A')}")
        print(f"  市盈率TTM: {data.get('市盈率TTM', 'N/A')}")
        print(f"  市净率: {data.get('市净率', 'N/A')}")
        print(f"  市销率: {data.get('市销率', 'N/A')}")
        print()

        # 市值信息
        print("🏢 市值信息:")
        print(f"  总市值: {data.get('总市值', 'N/A')}")
        print(f"  流通市值: {data.get('流通市值', 'N/A')}")
        print()

        # 技术指标
        print("📉 技术指标:")
        print(f"  量比: {data.get('量比', 'N/A')}")
        print(f"  委比: {data.get('委比', 'N/A')}")
        print(f"  振幅: {data.get('振幅', 'N/A')}")
        print(f"  涨速: {data.get('涨速', 'N/A')}")
        print()

        # 财务指标
        print("💼 财务指标:")
        print(f"  每股收益: {data.get('每股收益', 'N/A')}")
        print(f"  每股净资产: {data.get('每股净资产', 'N/A')}")
        print(f"  ROE: {data.get('ROE', 'N/A')}")
        print(f"  ROA: {data.get('ROA', 'N/A')}")
        print(f"  毛利率: {data.get('毛利率', 'N/A')}")
        print(f"  净利率: {data.get('净利率', 'N/A')}")
        print()

        # 资金流向
        print("💸 资金流向:")
        print(f"  主力净流入: {data.get('主力净流入', 'N/A')}")
        print(f"  超大单净流入: {data.get('超大单净流入', 'N/A')}")
        print(f"  大单净流入: {data.get('大单净流入', 'N/A')}")
        print(f"  中单净流入: {data.get('中单净流入', 'N/A')}")
        print(f"  小单净流入: {data.get('小单净流入', 'N/A')}")
        print()

        # 均线信息
        print("📊 均线信息:")
        print(f"  5日均线: {data.get('5日均线', 'N/A')}")
        print(f"  10日均线: {data.get('10日均线', 'N/A')}")
        print(f"  20日均线: {data.get('20日均线', 'N/A')}")
        print(f"  30日均线: {data.get('30日均线', 'N/A')}")
        print(f"  60日均线: {data.get('60日均线', 'N/A')}")
        print(f"  120日均线: {data.get('120日均线', 'N/A')}")
        print(f"  250日均线: {data.get('250日均线', 'N/A')}")
        print()

        # 显示所有可用字段
        print("📋 所有可用字段:")
        for key, value in data.items():
            if key not in ['股票代码', '股票名称', '数据来源', '数据时间戳']:
                print(f"  {key}: {value}")


def main():
    # 配置参数
    stock_code = "sz000498"  # 股票代码

    # 创建财务数据获取器
    fetcher = FinancialDataFetcher()

    # 获取财务数据
    print("🚀 获取财务数据...")
    financial_data = fetcher.get_financial_data(stock_code, data_source='auto')

    if financial_data:
        fetcher.print_financial_summary(financial_data)
        fetcher.save_to_json(financial_data, stock_code)
    else:
        print("❌ 无法获取财务数据")


if __name__ == "__main__":
    main()
